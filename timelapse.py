import datetime
import itertools
import json
import math
import os
import pathlib

import ffmpeg
import numpy as np
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageOps
from typing_extensions import OrderedDict

import utils

default_fonts = {"windows": "arial.ttf", "posix": "NotoSans-Regular.ttf"}


def timelapse_images(
    folders,
    video_size=(1920, 1080),
    output="./frameout/",
    **kwargs,
):
    outpath = pathlib.Path(output)
    outpath.mkdir(exist_ok=True)

    output_format = kwargs.get("output_format", "png")

    # n_frames = max([len(list(pathlib.Path(folder).glob("*.png"))) for folder in folders])

    for framed in timelapse_iterator(folders, video_size, **kwargs):
        frame = framed["frame"]
        name = framed["name"]
        fi = framed["frame_index"]
        fills = "".join(framed["fills"])
        utils.write(f"{fi:>6} | {name}\t{fills}")
        frame.save(outpath / (name + "." + output_format))
    utils.write(
        f"Finished!\nOutput written to {str(outpath)}\n"
        "You can convert the images to video using the following command:\n"
        f"> ffmpeg -framerate 30 -pattern_type glob -i '{output}/*.png' -c:v libx264 -pix_fmt yuv420p timelapse.mp4"
    )


def timelapse_ffmpeg(
    folders,
    video_size=(1920, 1080),
    output="./timelapse.mp4",
    **kwargs,
):
    outpath = pathlib.Path(output)
    outpath.parent.mkdir(exist_ok=True)

    framerate = kwargs.get("framerate", 30)

    ffproc = (
        ffmpeg.input(
            "pipe:",
            format="rawvideo",
            pix_fmt="rgb24",
            s=f"{video_size[0]}x{video_size[1]}",
            r=framerate,
        )
        .output(str(outpath), pix_fmt="yuv420p")
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    for frame in timelapse_iterator(folders, video_size, **kwargs):
        ffproc.stdin.write(np.array(frame["frame"]).astype(np.uint8).tobytes())

    ffproc.stdin.close()


def timelapse_iterator(folders, video_size=(1920, 1080), **kwargs):
    n_folders = len(folders)

    grid_size = math.ceil(math.sqrt(n_folders))

    width = video_size[0]
    height = video_size[1]
    cw = width // grid_size  # cell size
    ch = height // grid_size

    font = PIL.ImageFont.truetype(
        kwargs.get("font", default_fonts[os.name]),
        kwargs.get("font_size", 20),
    )

    timestamp = kwargs.get("timestamp", True)
    timestamp_pos = kwargs.get("timestamp_pos", (16, 16))
    timestamp_format = kwargs.get("timestamp_format", "%d %B, %Y\n%H:%M:%S")
    timestamp_color = kwargs.get("font_color", (255, 255, 255))

    captions = kwargs.get("captions", [""] * n_folders)
    skip = kwargs.get("skip", 0)
    fi = 0
    for name, files in synced_folder_iterator(folders):
        if fi < skip:
            fi += 1
            continue
        frame = PIL.Image.new("RGB", video_size)
        x = -1
        y = 0
        i = -1
        st = ["░"] * n_folders

        draw = PIL.ImageDraw.Draw(frame)

        for f, caption in zip(files, captions):
            x += 1
            i += 1
            if x >= grid_size:
                x = 0
                y += 1
            if f is not None:
                img = PIL.Image.open(f)
                img = PIL.ImageOps.cover(img, (cw, ch))
                PIL.Image.Image.paste(frame, img, (x * cw, y * ch))
                st[i] = "█"
            if caption != "":
                caption_pos = ((x + 1) * cw - 16, (y + 1) * ch - 16)
                draw.text(
                    caption_pos,
                    caption,
                    timestamp_color,
                    anchor="rb",
                    font=font,
                    stroke_width=1,
                    stroke_fill=(0, 0, 0),
                    **kwargs,
                )

        if timestamp:
            # Draw timestamp
            timestamp_ = datetime.datetime.strptime(name, "%d_%m_%y_%H_%M_%S")
            timestamp_str = timestamp_.strftime(timestamp_format)
            # draw.text((x, y),"Sample Text",(r,g,b))
            draw.text(
                timestamp_pos,
                timestamp_str,
                timestamp_color,
                font=font,
                stroke_width=1,
                stroke_fill=(0, 0, 0),
                **kwargs,
            )

        frame = {"name": name, "frame": frame, "fills": st, "frame_index": fi}
        fi += 1
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


def timelapse_from_config(config: dict):
    if config["output_format"] in ["ffmpeg", "mp4", "avi", "mkv", "mpg"]:
        timelapse_ffmpeg(**config)
    else:
        timelapse_images(**config)


def main():
    # Opening config file
    try:
        f = open("config.json")
        file_contents = str(f.read())
    except IOError | FileNotFoundError as e:
        utils.write(
            f"Failed to read config. File system / permission errors?\n{str(e)}"
        )
        return

    # Reading file as JSON data
    try:
        data = json.loads(file_contents)["timelapse"]
    except json.JSONDecodeError as e:
        utils.write(
            f"Failed to read config. Failed to interpret JSON structure. Is it in correct JSON syntax?\n{str(e)}"
        )
        return

    f.close()

    timelapse_from_config(data)


if __name__ == "__main__":
    main()
