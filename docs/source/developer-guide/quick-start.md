## 快速上手

### 搭建开发环境
1. 创建虚拟环境:

    ```shell
    conda create -n Groove python=3.8
    conda activate Groove
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

2. 下载解码器：
   * 对于 Win32，安装 [LAV Filters](https://github.com/Nevcairiel/LAVFilters/releases/download/0.74/LAVFilters-0.74-Installer.exe)
   * 对于 Linux，安装 GStreamer


3. 打开 Groove 音乐:

    ```shell
    cd app
    conda activate Groove
    python Groove.py
    ```

### VSCode 配置文件
这里提供几个使用 VSCode 开发时会用到的配置文件。

#### launch.json
`launch.json` 用来调试 Groove 音乐，需要在 VSCode 中将 Python 解释器切换为 `Groove` 虚拟环境下的解释器才能保证环境不出问题。
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "调试当前文件",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true,
            "cwd": "${fileDirname}"
        },
        {
            "name": "调试 Groove",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/app/Groove.py",
            "console": "integratedTerminal",
            "justMyCode": true,
        }
    ]
}
```

#### tasks.json
`tasks.json` 用来配置任务，一个任务对应着一条或者多条命令，这里总共配置了三个任务：`Run Groove`、`Compile qrc` 和 `Compile qrc and run Groove`：
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Groove",
            "detail": "运行 Groove 音乐",
            "type": "shell",
            "command": "D:/Anaconda/envs/Groove/python.exe",
            "args": ["Groove.py"],
            "problemMatcher": "$gcc",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "options": {
                "cwd": "${workspaceFolder}/app"
            }
        },
        {
            "label": "Compile qrc",
            "detail": "编译 qrc 文件",
            "type": "shell",
            "command": "pyrcc5",
            "args": [
                "-o",
                "../common/resource.py",
                "resource.qrc",
            ],
            "options": {
                "cwd": "${workspaceFolder}/app/resource"
            },
            "problemMatcher": "$gcc",
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "Compile qrc and run Groove",
            "detail": "编译 qrc 并运行 Groove 音乐",
            "type": "shell",
            "command": "D:/Anaconda/envs/Groove/python.exe",
            "args": ["Groove.py"],
            "problemMatcher": "$gcc",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "dependsOn": [
                "Compile qrc"
            ],
            "options": {
                "cwd": "${workspaceFolder}/app"
            }
        },
    ]
}
```

### 注意事项
1. 资源文件发生变更之后需要使用 `pyrcc5` 重新编译 `resource.qrc` 文件，生成的 `resource.py` 文件放在 `common` 文件夹下面