import math
import pathlib

import ffmpeg
import PIL.Image
import PIL.ImageOps
from PIL.ImageTransform import ExtentTransform
from typing_extensions import OrderedDict


def cut_timelapse(*folders, video_size=(1920, 1080)):

    n_folders = len(folders)

    grid_size = math.ceil(math.sqrt(n_folders))

    width = video_size[0]
    height = video_size[1]
    cw = width // grid_size  # cell size
    ch = height // grid_size

    for name, files in synced_folder_iterator(*folders):
        print(f"Frame {name}")
        frame = PIL.Image.new("RGB", video_size)
        x = -1
        y = 0
        for f in files:
            x += 1
            if x > grid_size:
                x = 0
                y += 1
            if f is None:
                continue
            img = PIL.Image.open(f)
            img = PIL.ImageOps.cover(img, (cw, ch))
            PIL.Image.Image.paste(frame, img, (x * cw, y * ch))
        frame.save("./videoout/" + name)


def synced_folder_iterator(*folders):
    png_iterators = OrderedDict()
    n_folders = len(folders)

    for folder in folders:
        folder = pathlib.Path(folder)
        png_iterators[folder] = iter(sorted(folder.glob("*.png", case_sensitive=False)))

    # the currently next images
    curr: list[pathlib.Path | None] = [None] * n_folders
    while True:
        for i, pi in enumerate(png_iterators.values()):
            # get some new images
            if curr[i] != None:
                # If there is still an image in the queue, skip  getting the next one
                continue
            try:
                curr[i] = next(pi)
            except StopIteration:
                curr[i] = None

        if all(c is None for c in curr):
            # all folders are empty
            return

        smallest = min([f.name for f in curr if f is not None])

        it: list[pathlib.Path | None] = []
        for i, c in enumerate(curr):
            if c is not None and c.name == smallest:
                it.append(c)
                curr[i] = None
            else:
                it.append(None)

        yield smallest, tuple(it)


if __name__ == "__main__":
    cut_timelapse("folder1", "folder2")
