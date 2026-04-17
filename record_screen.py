import json
import os
import time
from datetime import datetime, timedelta

import cv2
import numpy as np
from mss import mss

import share


def main():
    share.write('Welcome.')
    loop()


def loop():
    # =====================
    # Reading config
    # =====================
    share.write('Reading config.')
    f = open('config.json')
    data = json.loads(f.read())
    f.close()

    config_take_screenshot = bool(data["take_screenshot"])
    config_monitor_index = int(data["monitor_index"])
    config_take_webcam = bool(data["take_webcam"])
    config_webcam_index = int(data["webcam_index"])
    config_webcam_resolution_width = int(data["webcam_resolution_width"])
    config_webcam_resolution_height = int(data["webcam_resolution_height"])
    config_output_dir = str(data["output_dir"])
    screenshots_per_minute = int(str(data["screenshots_per_minute"]))

    cap = None
    if config_take_webcam:
        share.write('Setting up Webcam.')
        cap = cv2.VideoCapture(config_webcam_index)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config_webcam_resolution_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config_webcam_resolution_height)

        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        share.write(f"Webcam Resolution: {int(width)}x{int(height)}")

    if screenshots_per_minute <= 0:
        raise ValueError("rate_per_minute must be greater than 0")

    if 60 % screenshots_per_minute != 0:
        raise ValueError(
            "Screenshots per minute must be a divisor of 60 "
            "(e.g. 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60)"
        )

    interval_seconds = 60 // screenshots_per_minute

    while True:
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

        if config_take_screenshot:
            try:
                take_screenshot(out_file_dir=config_output_dir, monitor_index=config_monitor_index)
            except Exception as e:
                share.write('Error while taking screenshot.')

        if config_take_webcam:
            try:
                record_webcam(out_file_dir=config_output_dir, cap=cap)
            except Exception as e:
                share.write('Error while taking screenshot.')


def take_screenshot(out_file_dir: str, monitor_index=0):
    img = None
    with mss() as sct:
        monitor_2 = sct.monitors[monitor_index]
        shot = sct.grab(monitor_2)
        img = np.array(shot)

    path = os.path.abspath(out_file_dir)
    os.makedirs(path, exist_ok=True)

    timestamp = datetime.now().strftime("%d_%m_%y_%H_%M_%S")
    file_name = f'{path}{os.sep}screenshot_{timestamp}.png'

    cv2.imwrite(file_name, img)
    share.write(f'File saved: {file_name}')


def record_webcam(out_file_dir: str, cap):
    ret, frame = cap.read()
    if not ret:
        share.write("Failed to capture webcam.")
        return

    path = os.path.abspath(out_file_dir)
    os.makedirs(path, exist_ok=True)
    timestamp = datetime.now().strftime("%d_%m_%y_%H_%M_%S")
    file_name = f'{path}{os.sep}webcam_{timestamp}.png'
    cv2.imwrite(file_name, frame)
    share.write(f'File saved: {file_name}')


if __name__ == '__main__':
    main()
