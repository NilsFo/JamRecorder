import json
import os
import time
from datetime import datetime

import cv2
import numpy as np
from mss import mss

import share


def main():
    share.write('Welcome.')

    loop(screenshots_per_minute=20)


def loop(screenshots_per_minute):
    interval = 60.0 / screenshots_per_minute  # seconds between triggers
    next_trigger_time = time.perf_counter()

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

    cap = None
    if config_take_webcam:
        share.write('Setting up Webcam.')
        cap = cv2.VideoCapture(config_webcam_index)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config_webcam_resolution_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config_webcam_resolution_height)

        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        share.write(f"Webcam Resolution: {int(width)}x{int(height)}")

    # =====================
    # MAIN LOOP
    # =====================

    while True:
        # --- TRIGGER ACTION ---
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
        # Replace this with your actual logic

        # --- SCHEDULING ---
        next_trigger_time += interval
        sleep_time = next_trigger_time - time.perf_counter()

        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            # We're behind schedule; skip sleep and resync
            next_trigger_time = time.perf_counter()


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
