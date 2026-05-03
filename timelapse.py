import itertools
import math
import pathlib

import PIL.Image
import PIL.ImageOps
import ffmpeg
import numpy as np
from typing_extensions import OrderedDict


def timelapse_images(folders, video_size=(1920, 1080), output_folder="./frameout/"):
    outpath = pathlib.Path(output_folder)
    outpath.mkdir(exist_ok=True)

    # n_frames = max(
    #     [len(list(pathlib.Path(folder).glob("*.png"))) for folder in folders]
    # )
    fi = 0

    for framed in timelapse_iterator(folders, video_size):
        frame = framed["frame"]
        name = framed["name"]
        fills = "".join(framed["fills"])
        print(f"{fi:>6} | {name}\t{fills}")
        frame.save(outpath / (name + ".png"))
        fi += 1


def timelapse_ffmpeg(
        folders, video_size=(1920, 1080), output_file="./timelapse.mp4", framerate=30
):
    outpath = pathlib.Path(output_file)
    outpath.parent.mkdir(exist_ok=True)

    ffproc = (
        ffmpeg.input(
            "pipe:",
            format="rawvideo",
            pix_fmt="rgb24",
            s=f"{video_size[0]}x{video_size[1]}",
        )
        .output(str(outpath), pix_fmt="yuv420p")
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    for frame in timelapse_iterator(folders, video_size):
        ffproc.stdin.write(np.array(frame["frame"]).astype(np.uint8).tobytes())

    ffproc.stdin.close()


def timelapse_iterator(folders, video_size=(1920, 1080)):
    n_folders = len(folders)

    grid_size = math.ceil(math.sqrt(n_folders))

    width = video_size[0]
    height = video_size[1]
    cw = width // grid_size  # cell size
    ch = height // grid_size

    for name, files in synced_folder_iterator(folders):
        # print(f"Frame {name}")
        frame = PIL.Image.new("RGB", video_size)
        x = -1
        y = 0
        i = -1
        st = ["░"] * n_folders
        for f in files:
            x += 1
            i += 1
            if x >= grid_size:
                x = 0
                y += 1
            if f is None:
                continue
            img = PIL.Image.open(f)
            img = PIL.ImageOps.cover(img, (cw, ch))
            PIL.Image.Image.paste(frame, img, (x * cw, y * ch))
            st[i] = "█"
        frame = {"name": name, "frame": frame, "fills": st}
        yield frame


def synced_folder_iterator(folders):
    img_iterators = OrderedDict()
    n_folders = len(folders)

    for folder in folders:
        folder = pathlib.Path(folder)
        pngs = folder.glob("*.png", case_sensitive=False)
        jpgs = folder.glob("*.jpg", case_sensitive=False)
        img_iterators[folder] = iter(sorted(itertools.chain(pngs, jpgs)))

    # the currently next images
    curr: list[pathlib.Path | None] = [None] * n_folders
    while True:
        for i, pi in enumerate(img_iterators.values()):
            # get some new images
            if curr[i] is not None:
                # If there is still an image in the queue, skip  getting the next one
                continue
            try:
                curr[i] = next(pi)
            except StopIteration:
                curr[i] = None

        if all(c is None for c in curr):
            # all folders are empty
            return

        # get the non-processed image with the lowest time
        smallest = min([f.stem[-17:] for f in curr if f is not None])

        # get all images that share this timestamp
        it: list[pathlib.Path | None] = []
        for i, c in enumerate(curr):
            if c is not None and c.stem[-17:] == smallest:
                it.append(c)
                curr[i] = None
            else:
                it.append(None)

        yield smallest, tuple(it)


if __name__ == "__main__":
    timelapse_images(
        ["recording/Webcam", "recording/Adi", "recording/ph", "recording/Nils"]
    )
