<p align="center">
  <img width="12%" align="center" src="app/resource/images/logo/logo.png" alt="logo">
</p>
  <h1 align="center">
  Groove Music
</h1>
<p align="center">
  A cross-platform music player based on PyQt5.
</p>

<p align="center">

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Python-3.8.6-blue.svg?color=00B16A" alt="Python 3.8.6"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/PyQt-5.15.2-blue?color=00B16A" alt="PyQt 5.15.2"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Platform-Win32%20|%20Linux%20|%20macOS-blue?color=00B16A" alt="Platform Win32 | Linux | macOS"/>
  </a>
</p>

<p align="center">
English | <a href="docs/README_zh.md">简体中文</a>
</p>

## Interface
![界面](docs/screenshot/Groove音乐.png)

## Features

* Play local music

  ![local music](docs/screenshot/本地音乐.gif)

* Search, play and download online music

  ![online music](docs/screenshot/在线音乐.gif)

* Create and manage custom playlist

  ![custom playlist](docs/screenshot/播放列表.gif)

* View and edit song meta data

  ![song meta data](docs/screenshot/歌曲信息.gif)

* Watch and download MV

  ![MV](docs/screenshot/播放和下载MV.png)



## Quick start
1. Create virtual environment:

    ```shell
    conda create -n Groove python=3.8
    conda activate Groove
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

2. Download decoder:
   * For the Win32, you should install [LAV Filters](https://github.com/Nevcairiel/LAVFilters/releases/download/0.74/LAVFilters-0.74-Installer.exe).
   * For the Linux, you should install GStreamer.

3. Open Groove music:

    ```shell
    cd app
    conda activate Groove
    python Groove.py
    ```

## Install
### Win32
#### Installer
1. Download and install [LAV Filters](https://github.com/Nevcairiel/LAVFilters/releases/download/0.74/LAVFilters-0.74-Installer.exe)
2. Download `Groove_v*.*.*_x64_setup.exe` from [release page](https://github.com/zhiyiYo/Groove/releases)
3. Run `Groove_v*.*.*_x64_setup.exe` as administrator and install Groove
4. Start to enjoy your music~~

#### Portable Edition
1. Download and install [LAV Filters](https://github.com/Nevcairiel/LAVFilters/releases/download/0.74/LAVFilters-0.74-Installer.exe)
2. Download `Groove_v*.*.*_windows_x64.zip` from [release page](https://github.com/zhiyiYo/Groove/releases)
3. Unzip `Groove_v*.*.*_windows_x64.zip`
4. Go to `Groove` folder, find and double click **Groove.exe**
5. Start to enjoy your music~~

### Linux
1. Install GStreamer
2. Download `Groove_v*.*.*_linux_x64.zip` from [release page](https://github.com/zhiyiYo/Groove/releases)
3. Unzip `Groove_v*.*.*_linux_x64.zip`
4. Go to `Groove` folder, find and double click the **Groove** executable file
5. Start to enjoy your music~~


## FAQ
* **Why does the window get stuck when it is dragged?**

  Because the interface background uses acrylic effect, this problem will occur for some versions of win10. There are three solutions:

  * Upgrade Win10 to Win11.
  * Uncheck the check box of **Advanced system settings --> Performance --> Show window contents when dragging**.
  * Turn off the option to enable acrylic background in the setting interface.

* **What formats of audio files are supported?**

  Currently, the following formats are supported:
  * True Audio File(*.tta)
  * WAVE Audio File(*.wav)
  * WavPack Audio File(*.wv)
  * Audio Codec 3 File(*.ac3)
  * Ogg Opus Audio File(*.opus)
  * Ogg Vorbis Audio File(*.ogg)
  * MPEG File(*.mp3, *.m4a, *.mp4)
  * Windows Media Audio File(*.wma)
  * Advanced Audio Coding File(*.aac)
  * Advanced Systems Format File(*.asf)
  * Audio Interchange File Format(*.aiff)
  * Free Lossless Audio Codec File(*.flac)
  * Musepack Compressed Audio File(*.mpc)
  * Monkey's Audio Lossless Audio File(*.ape)

* **Why did GStreamer report this error: Warning: "No decoder available for type blah blah"?**

  I solved this problem on Ubuntu 20.04 by `sudo apt-get install gstreamer1.0-libav`.

* **What formats of lyrics files are supported?**

  Currently, lyrics in `.lrc` format and `.json` format are supported. Refer to [lyrics file format](./docs/lyrics_format.md) for more information.

