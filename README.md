<p align="center">
  <img width="15%" align="center" src="app/resource/images/logo/logo.png" alt="logo">
</p>
  <h1 align="center">
  Groove Music
</h1>
<p align="center">
  A cross-platform music player based on PyQt5
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

![界面](docs/source/_static/images/Groove音乐.jpg)

## Features

* Play local music

  ![local music](docs/source/_static/images/本地音乐.gif)

* Create and manage custom playlist

  ![custom playlist](docs/source/_static/images/播放列表.gif)

* View and edit song meta data

  ![song meta data](docs/source/_static/images/歌曲信息.gif)

* Watch and download MV

  ![MV](docs/source/_static/images/播放和下载MV.jpg)



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


## Document
Want to know more about Groove Music? Please read the [help document](https://groove-music.readthedocs.io) 👈

## See also

- [zhiyiYo/PyQt-Frameless-Window](https://github.com/zhiyiYo/PyQt-Frameless-Window)：A cross-platform frameless window based on pyqt5, support Win32, Linux and macOS.
- [zhiyiYo/PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)：A fluent design widgets library based on PyQt5
- [jsmolka/egg-player](https://github.com/jsmolka/egg-player)：A Groove Music like music player. The code of this repo is very elegant.

## License
Groove is licensed under GPLv3 for non-commercial usage.

Copyright © 2020 by zhiyiYo.

> *Attention*
>
> This software is only for learning and communication, the songs' and playlists' copyright belongs to each music platform.