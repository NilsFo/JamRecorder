# Jam Recorder


[![Language](https://img.shields.io/github/languages/top/NilsFo/JamRecorder?style=flat)](https://github.com/NilsFo/JamRecorder)

[![GitHub Stars](https://img.shields.io/github/stars/NilsFo/JamRecorder.svg?style=social&label=Star)](https://github.com/NilsFo/JamRecorder) 
&nbsp;
[![GitHub Downloads](https://img.shields.io/github/downloads/NilsFo/JamRecorder/total?style=social)](https://github.com/NilsFo/JamRecorder/releases) 

![License](https://img.shields.io/github/license/NilsFo/JamRecorder)
&nbsp;
![Size](https://img.shields.io/github/repo-size/NilsFo/JamRecorder?style=flat)
&nbsp;
[![Issues](https://img.shields.io/github/issues/NilsFo/JamRecorder?style=flat)](https://github.com/NilsFo/JamRecorder/issues)
&nbsp;

***

<!-- TOC -->
* [Jam Recorder](#jam-recorder)
  * [General](#general)
  * [Setup](#setup)
    * [Compatability](#compatability)
    * [Issues and Errors](#issues-and-errors)
  * [Recording](#recording)
    * [Config](#config)
    * [Screenshots](#screenshots)
    * [Webcam](#webcam)
  * [Creating a timelapse](#creating-a-timelapse)
* [License](#license)
<!-- TOC -->

## General

Records your screen or your webcam so can create a timelapse later.
Images are created at a specific interval to sync screenshots and webcam recordings between devices.
Intended use is to run locally on different devices.
Images can be stitched together afterward to render a timelapse video.

## Setup

Requires Python `3.10`.

Best used with [uv](https://docs.astral.sh/uv/) to generate the virtual environment to run.
Run `$ uv sync` to automatically set up everything for you.

### Compatability
This tool is designed and tested to be run on MS Windows and Linux alike.
No special precautions must be taken for this to run on each platform.

### Issues and Errors
If you encounter any irregularities, issues, errors, etc. please report them in [our issue section](https://github.com/NilsFo/JamRecorder/issues).
Please report any contradictions in this `README.md`.

## Recording
Before you can create a timelapse you should create some recordings.
Run `$ python record_screen.py` to begin recording.

An infinite loop is started and recordings are placed in a specified directory at the moment they are created.
Quit the loop by terminating the program.

### Config
You can specify parameters for recording from a config file.
Place a `config.json` file in the root directory.
In the project root is an example with default parameters.
If you do not specify a config, the example will be used.

Familiarize yourself with the parameters:
- `take_screenshot` (type: `int`): Intended as a `bool`. If `1` screenshots are taken.
- `monitor_index` (type: `int`): The index of the monitor to take screenshots.
- `take_webcam` (type: `int`): Intended as a `bool`. If `1` takes webcam recordings.
- `webcam_index` (type: `int`): The index of the webcam to take recordings from.
- `webcam_resolution_width` (type: `int`): The width of the image taken from the webcam.
- `webcam_resolution_height` (type: `int`): The height of the image taken from the webcam.
- `output_dir` (type: `str`): The directory where to store recordings in.
- `recordings_per_minute` (type: `int`): The frequency of recordings to be taken per minute.

If the output directory does not exist, it will be created.

The recordings intended to be synced across multiple devices running instances of this project.
So they are designed to trigger at full seconds.
As a result, valid values for `recordings_per_minute` must be a divisor of `60` (e.g. `1`, `2`, `3`, `4`, `5`, `6`, `10`, `12`, `15`, `20`, `30`, `60`).

### Screenshots
Exactly one single screen can be used to take screenshots from.
The `monitor_index` reflects the index of the monitor to access.
If you have a multi-monitor setup, this value should correspond with the monitor index assigned by your operating system.

### Webcam
If you have a webcam or other optical recording device you can access it alongside taking screenshots to generate frames for your timelapse.
For devices with a builtin webcam (e.g. a laptop) external webcams are also supported.
You can select what webcam to access via the `webcam_index` parameter in the `config.json`.

Exactly one webcam can be accessed at a time for this project.
You can select the recording resolution via the `webcam_resolution_width` and `webcam_resolution_height` parameters.
**NOTE**:
This is usually corrected / rounded to the nearest supported resolution, determined by your operating system's drivers and the device's supported resolutions.

## Creating a timelapse

TBA.

# License

See `LICENSE.md` in the root directory.
