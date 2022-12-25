## 歌词文件
Groove 音乐支持 `lrc` 格式和 `json` 格式的歌词文件。

### lrc 格式
歌词格式为 **[mm:ss.xx]**，其中 **mm** 为分钟，**ss** 为秒，**xx** 为百分之一秒，更多关于 `lrc` 格式的信息可以参见 [维基百科](https://zh.wikipedia.org/wiki/LRC%E6%A0%BC%E5%BC%8F)。下面是一个例子：
```
[ti:Lyric Demo]
[ar:zhiyiYo]
[au:Written by zhiyiYo, 2022]
[al:Groove - Vol. 2 – Melody]

[00:12.00]zhiyiYo - Lyric Demo
[00:15.30]hello
[00:15.30]你好 # 重复时间标签来添加翻译
[01:02.30]world
[01:04.29]我家硝子真卡哇伊🥰
```

### json 格式
歌词格式为 **"seconds":["orginal lyric"]** 或者 **"seconds":["orginal lyric", "translation lyric"]**。如下所示：
```json
{
    "1.86": [
        "微熱 - Aiko "
    ],
    "3.7": [
        "词：aiko"
    ],
    "6.49": [
        "曲：aiko"
    ],
    "28.22": [
        "今夜も必ず連絡するね",
        "今夜也一定会和我联系"
    ],
    "34.36": [
        "昼も夜も抱きしめて",
        "又能相拥一夜"
    ],
}
```
