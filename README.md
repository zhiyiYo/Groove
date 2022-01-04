<p align="center">
  <img width="12%" align="center" src="app/resource/images/logo/logo.png" alt="logo">
</p>
  <h1 align="center">
  Groove Music
</h1>
<p align="center">
  A music player based on PyQt5 and LAV Filters.
</p>

<p align="center">

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Python-3.8.6-blue.svg?color=00B16A" alt="Python 3.8.6"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/PyQt-5.15.2-blue?color=00B16A" alt="PyQt 5.15.2"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/LAV%20Filters-0.74.1-blue?color=00B16A" alt="LAV Filters 0.74.1"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/OS-Win%2010%20|%20Win%2011-blue?color=00B16A" alt="OS Win10 | Win11"/>
  </a>
</p>

## Interface
![界面](docs/screenshot/Groove音乐.png)

## Features

* Play local music
![播放本地音乐](docs/screenshot/播放本地音乐.gif)

* Search, play and download online music
![搜索播放和下载在线音乐](docs/screenshot/搜索播放和下载在线音乐.gif)

* Create playlist
![创建播放列表](docs/screenshot/创建播放列表.gif)

* View and edit information
![编辑歌曲和专辑信息](docs/screenshot/编辑歌曲和专辑信息.gif)

* Automatically retrieve and update missing metadata
![爬虫](docs/screenshot/爬取歌曲信息.gif)

## Quick start
1. Create virtual environment:

    ```shell
    conda create -n Groove python=3.8
    conda activate Groove
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

2. Download [LAV Filters](https://github.com/Nevcairiel/LAVFilters/releases).
3. Open Groove music:

    ```shell
    cd app
    conda activate Groove
    python Groove.py
    ```


## FAQ
* **Why does the window get stuck when it is dragged?**

  Because the interface background uses acrylic effect, this problem will occur for some versions of win10. There are three solutions:

  * Upgrade win10 to the latest version.
  * Uncheck the check box of **Advanced system settings --> Performance --> Show window contents when dragging**.
  * Turn off the option to enable acrylic background in the setting interface.

* **What formats of audio files are supported?**

  Currently, the following audio files are supported:
  * mp3
  * flac
  * mp4/m4a
