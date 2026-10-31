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
Run `$ python record.py` to begin recording.

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

Once you have some recordings from one or multiple devices, you can create a simultaneous timelapse using `timelapse.py`.
Copy the recording folders from other devices into your recordings folder, so that each view has its own folder.
The timelapse script will order the views into a grid (2x2, 3x3, etc.) and synchronize all of them.
Configure the settings of the timelapse using your `config.json` like this:

```json
  "timelapse": {
    "output_format": "ffmpeg",    // "ffmpeg" for direct-to-video, or "png" for individual frames
    "output": "timelapse.mp4",    // output file (for video) or output folder (for individual frames)
    "output_size": [1920, 1080],  // Resolution of the output images/video
    "folders": [                  // The folders for the recordings, corresponding to a view in the grid
        "recordings/myrecording", 
        "recordings/bob", 
        "recordings/oscar", 
        "recordings/webcam"
    ],
    "captions": ["Alice", "Bob", "Oscar", "Webcam"],  // Caption in the bottom right of each view
    "draw_timestamp": true,           // Renders the timestamp into the output
    "timestamp_position": [16, 16],   // Position of the timestamp (top left)
    "timestamp_format": "%d %B, %Y\n%H:%M",  // Format of the timestamp
    "font_size": 24,                  // Font size for time stamp and captions
    "font_name": "arial.ttf",         // Font for time stamp and captions
    "font_color": [255, 255, 255],    // Font color for time stamp and captions
    "framerate": 30                   // Framerate
  }
```

Then, run `python timelapse.py config.json` or `uv run timelapse.py config.json` to start the timelapsing.
If you are using the ffmpeg option, make sure [ffmpeg](https://ffmpeg.org/) is installed and `ffmpeg` is in the path.
If you are using the png output format, you can then create a video from the pngs using ffmpeg like this:

```sh
ffmpeg -framerate 30 -pattern_type glob -i '{output}/*.png' -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```



# License

See `LICENSE.md` in the root directory.
