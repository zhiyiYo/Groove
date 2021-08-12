<p align="center">
  <img width="12%" align="center" src="app/resource/images/logo.png" alt="logo">
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
    <img src="https://img.shields.io/badge/PyQt-5.13.2-blue?color=00B16A" alt="PyQt 5.13.2"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/LAV%20Filters-0.74.1-blue?color=00B16A" alt="OS Win10 | Windows11"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/OS-Win%2010%20|%20Win%2011-blue?color=00B16A" alt="OS Win10 | Windows11"/>
  </a>
</p>

## Interface
![界面](docs/screenshot/Groove音乐.png)

## Features

* Play music
![播放本地音乐](docs/screenshot/播放本地音乐.gif)

* Create playlist
![创建播放列表](docs/screenshot/创建播放列表.gif)

* View and edit information
![编辑信息](docs/screenshot/编辑信息.gif)

* Automatically retrieve and update missing metadata
![爬虫](docs/screenshot/爬虫.gif)

## Quick start
1. Create virtual environment:

    ```shell
    conda create -n Groove python=3.8
    conda activate Groove
    pip install -r requirements.txt
    ```

2. Download [LAV Filters](https://github.com/Nevcairiel/LAVFilters/releases).
3. (Optional) Download `Firefox` and `geckodriver.exe`.
4. Open Groove music:

    ```shell
    conda activate Groove
    python Groove.py
    ```

## Notes
* If you want to use the function of automatically obtaining song metadata, you need to download `Firefox` and `geckodriver.exe`, then add the directory of geckodriver.exe to the environment variable.
