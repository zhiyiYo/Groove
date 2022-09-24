## lrc format
if the format of lyrics file is `.lrc`, then the structure should be like **[mm:ss.xx]**, where mm is minutes, ss is seconds and xx is hundredths of a second. You can refer to [wikipedia](https://en.wikipedia.org/wiki/LRC_(file_format)) for more information about `.lrc` format. Here is an example:
```
[ti:Let's Twist Again]
[ar:Chubby Checker oppure  Beatles, The]
[au:Written by Kal Mann / Dave Appell, 1961]
[al:Hits Of The 60's - Vol. 2 – Oldies]

[00:12.00]Naku Penda Piya-Naku Taka Piya-Mpenziwe
[00:15.30]hello
[00:15.30]你好 # you can duplicate the time tag to add translation
[01:02.30]world
[01:04.29]Shoko is so kawaii🥰
```

## json format
if the format is `.json`, then the structure should be like **"seconds":["orginal lyric"]** or **"seconds":["orginal lyric", "translation lyric"]**.
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
