## 常见问题

### 为什么窗口拖动的时候会出现卡顿现象？

  由于界面使用了亚克力窗口特效，在某些版本的 Win10 上会出现这个问题。有三种解决方案:

  * 更新 Win10 到最新版本，比如 Win11.
  * 取消复选框的选中 **高级系统设置 --> 性能 --> 拖动时显示窗口内容**.
  * 在设置界面禁用亚克力效果.

### 为什么运行的时候 GStreamer 报错：Warning: "No decoder available for type ..."?

  可以尝试 `sudo apt-get install gstreamer1.0-libav` 来解决该问题，Ubuntu 20.04 亲测有效。

### 支持哪些格式的歌词文件呀？

  目前支持 `.lrc` 和 `.json` 格式的歌词文件，更多信息请参见 [歌词文件格式说明](./lyrics-format.md)。