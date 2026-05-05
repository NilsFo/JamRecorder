"""
record.py

Screen recording utility.

This module reads configuration from ``config.json`` and starts an endless recording
loop that captures screen frames or webcam images.
Images are written at a specified interval so they can be synced across multiple instances / users.
They are written to a specified directory.

Typical usage:
    python record.py

The main entry point is ``main()``.
"""

import json
import os
import shutil
import time
from datetime import datetime, timedelta

import cv2
import numpy as np
from mss import mss

import utils

"""
Start the recording program.

Writes a welcome message and then enters the main recording loop.

Returns:
    None
"""


def main():
    utils.write("Welcome.")
    loop()


def loop():
    """
    Run the main recording loop.

    Reads configuration from ``config.json`` in the current working directory and then continues with the
    program's recording workflow.

    Configuration:
        The function expects a file named ``config.json`` to exist in the
        current working directory.

    Returns:
        None

    Raises:
        FileNotFoundError: If ``config.json`` is required later and cannot be found or read.
        json.JSONDecodeError: If the config file contains invalid JSON.

    """

    # ================================================================================================
    # Reading config
    # ================================================================================================
    config_file_path = os.path.abspath("config.json")
    utils.write(f"Reading config: {config_file_path}")

    if not os.path.exists(config_file_path):
        # user config file does not exist. we'll copy default config instead
        shutil.copy("example_config.json", "config.json")

    # Opening config file
    try:
        f = open("config.json")
        file_contents = str(f.read())
    except IOError | FileNotFoundError as e:
        utils.write(f"Failed to read config. File system / permission errors?")
        return

    # Reading file as JSON data
    try:
        data = json.loads(file_contents)["recordings"]
    except json.JSONDecodeError as e:
        utils.write(
            f"Failed to read config. Failed to interpret JSON structure. Is it in correct JSON syntax?"
        )
        return

    f.close()

    config_record_screenshot = bool(int(data["record_screenshot"]))
    config_monitor_index = int(data["monitor_index"])
    config_record_webcam = bool(int(data["record_webcam"]))
    config_webcam_index = int(data["webcam_index"])
    config_webcam_resolution_width = int(data["webcam_resolution_width"])
    config_webcam_resolution_height = int(data["webcam_resolution_height"])
    config_output_dir = str(data["output_dir"])
    recordings_per_minute = int(str(data["recordings_per_minute"]))

    # ================================================================================================
    # Setting up Webcam
    # ================================================================================================
    cap = None
    if config_record_webcam:
        utils.write("Setting up Webcam.")
        cap = cv2.VideoCapture(config_webcam_index)

    if cap is None:
        # We could not access the webcam. Disabling command.
        config_take_webcam = False
        utils.write("Failed to access Webcam.")
    else:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config_webcam_resolution_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config_webcam_resolution_height)

        # Reading the width / height back to the user, as CV2 may not directly translate to webcam hardware.
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        utils.write(f"Webcam Resolution: {int(width)}x{int(height)}")

    # ================================================================================================
    # Setting up Loop
    # ================================================================================================
    if recordings_per_minute <= 0:
        raise ValueError("rate_per_minute must be greater than 0")

    if 60 % recordings_per_minute != 0:
        raise ValueError(
            "Recordings per minute must be a divisor of 60 "
            "(e.g. 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60)!"
        )

    interval_seconds = 60 // recordings_per_minute

    # ================================================================================================
    # Main Loop
    # ================================================================================================
    while True:
        # =============================================================================================
        # Waiting for next timestamp
        # =============================================================================================
        now = datetime.now()

        # Start of the current minute
        minute_start = now.replace(second=0, microsecond=0)

        # Seconds elapsed since minute start
        elapsed_seconds = now.second + now.microsecond / 1_000_000

        # Find next aligned trigger slot
        next_slot = int(elapsed_seconds // interval_seconds) + 1
        next_trigger = minute_start + timedelta(seconds=next_slot * interval_seconds)

        # If we've crossed into the next minute, that's fine;
        # datetime handles it automatically.
        sleep_seconds = (next_trigger - now).total_seconds()

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

        # =============================================================================================
        # Recording Screenshots
        # =============================================================================================
        if config_record_screenshot:
            try:
                take_screenshot(
                    out_file_dir=config_output_dir,
                    monitor_index=config_monitor_index
                )
            except Exception as e:
                utils.write(f"Error while taking screenshot. {e}")

        # =============================================================================================
        # Reading from the Webcam
        # =============================================================================================
        if config_record_webcam:
            try:
                record_webcam(
                    out_file_dir=config_output_dir,
                    cap=cap
                )
            except Exception as e:
                utils.write(f"Error while taking webcam photo. {e}")


def take_screenshot(
        out_file_dir: str,
        monitor_index=0
):
    """
    Takes a screenshot and saves it to a specified directory.
    File name is automatically chosen based on current time.

    Args:
        out_file_dir: Directory where the screenshot file should be written.
        monitor_index: Index of the monitor to capture. Defaults to ``0``.
            The exact monitor indexing depends on the screen-capture backend.

    Returns:
        None
    """

    img = None
    # using mss to take a screenshot of a specified monitor index
    with mss() as sct:
        monitor_2 = sct.monitors[monitor_index]
        shot = sct.grab(monitor_2)
        img = np.array(shot)

    # get the full file name and path to save the file to
    file_name = _out_file_name(
        out_file_dir=out_file_dir,
        file_name_prefix='screenshot',
        file_name_suffix='',
        file_extension='png'
    )

    # writes the image (without alpha channel) to disk
    cv2.imwrite(file_name, img[..., :3])
    utils.write(f"File saved: {file_name}")


def record_webcam(
        out_file_dir: str,
        cap: cv2.VideoCapture
):
    """
    Takes frame from the selected webcam and saves it to a specified directory.
    File name is automatically chosen based on current time.
    Actually it takes a generic `cv2.VideoCapture` as an input so it could be any supported video stream.

    Args:
        out_file_dir: Directory where the frame file should be written.
        cap: Existing video input stream to take a frame from.
             Do not close it while you want to capture from it.

    Returns:
        None
    """

    # gets the current frame from the webcam stream
    ret, frame = cap.read()
    if not ret:
        utils.write("Failed to capture webcam.")
        return

    # get the full file name and path to save the file to
    file_name = _out_file_name(
        out_file_dir=out_file_dir,
        file_name_prefix='webcam',
        file_name_suffix='',
        file_extension='jpg'
    )

    # writes the image (without alpha channel) to disk
    cv2.imwrite(file_name, frame[..., :3])
    utils.write(f"File saved: {file_name}")


def _out_file_name(
        out_file_dir: str,
        file_name_prefix: str,
        file_name_suffix: str,
        file_extension: str
):
    """
    Internal function to generate the full path for a file name.
    Intended to sync file naming structure between different forms of recording (e.g. screenshot and webcam).

    File name is based on an input directory and the current time.
    You can specify a _prefix_ and _suffix_ to specify the intended file "type", e.g. the capture method.

    In general, the pattern looks

    Args:
        out_file_dir: Directory where the frame file should be written. If it does not exist, it will be created.
        file_name_prefix: A prefix to be used before the timestamp.
        file_name_suffix: A suffix to be used after the timestamp.
        file_extension: The file type. Common values are `png`, `jpg`, etc. No need to specify the file separator char.

    Returns:
        The full file path of the file to be saved.
    """

    # setup directory to save screenshot in
    path = os.path.abspath(out_file_dir)
    os.makedirs(path, exist_ok=True)

    # generates the file name for the image
    timestamp = datetime.now().strftime("%d_%m_%y_%H_%M_%S")
    file_name = f"{path}{os.sep}{file_name_prefix}_{timestamp}{file_name_suffix}.{file_extension}"
    return file_name


if __name__ == "__main__":
    main()
