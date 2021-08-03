# Groove
A music player based on pyqt5 and LAV Filters.

## Interface
![界面](docs/screenshot/Groove音乐.png)

## Features

* Play music
![示例动图1](docs/screenshot/播放本地音乐.gif)

* Create playlist
![示例动图2](docs/screenshot/创建播放列表.gif)

* View and edit information
![示例动图3](docs/screenshot/编辑信息.gif)

* Automatically retrieve and update missing metadata
![示例动图4](docs/screenshot/爬虫.gif)

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
