# 韩文视频双语字幕生成器

上传视频 / 音频 / 粘贴链接，自动生成「韩文 + 中文」双语 SRT 字幕文件，并在浏览器中实时预览。

---

## 效果预览

- 输入：韩文视频（本地文件 / TikTok / YouTube 等链接）
- 输出：字幕烧录预览视频 + 可下载的 `.srt` 双语字幕文件

```
1
00:00:00,000 --> 00:00:02,600
요즘 상하이 여행 왜 이렇게 많이 가요?
为什么最近这么多人去上海旅游？
```

---

## 环境要求

| 项目 | 要求 |
|------|------|
| Python | 3.9 或以上 |
| 内存 | 8GB+（large-v3 模型需要约 4GB） |
| 网络 | 首次运行需下载模型（约 3GB） |
| 显卡 | 无也可以，有 Nvidia GPU 速度更快 |

---

## 一、安装 Git

### Windows

1. 打开 https://git-scm.com/download/win
2. 下载安装包，一路点 Next（所有选项保持默认）
3. 安装完成后重启终端

### Mac

```bash
brew install git
```

---

## 二、安装 Python

### Windows

1. 打开 https://www.python.org/downloads/
2. 点击 **Download Python 3.x.x**，下载安装包
3. 安装时勾选 ✅ **Add Python to PATH**（重要！）
4. 一路点 Next 完成安装

### Mac

打开终端（Terminal），执行：

```bash
brew install python
```

没有 Homebrew？先执行：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## 三、安装 FFmpeg

FFmpeg 用于把字幕烧录进预览视频。

### Windows

```powershell
winget install Gyan.FFmpeg
```

安装后**重启终端**。

### Mac

```bash
brew install ffmpeg
```

---

## 四、下载项目 & 安装依赖

```bash
# 克隆项目
git clone https://github.com/lizaicheng/korean-subtitle-gen.git
cd korean-subtitle-gen

# 安装 Python 依赖
pip install faster-whisper deep-translator gradio yt-dlp
```

---

## 五、启动

```bash
python app.py
```

首次启动会自动下载 **Whisper large-v3 模型**（约 3GB），下载完成后缓存在本地，之后无需重复下载。

下载完成后，浏览器会自动打开，或手动访问：

```
http://localhost:7860
```

---

## 六、使用方式

界面分三个功能 Tab：

| Tab | 说明 |
|-----|------|
| 🔗 粘贴链接 | 粘贴 TikTok / YouTube / 抖音等视频链接，自动下载并生成字幕 |
| 📁 上传视频 | 上传本地 `.mp4 .mkv .avi .mov .webm` 视频文件 |
| 🎵 上传音频 | 上传本地 `.mp3 .wav .m4a .aac .flac` 音频文件 |

处理完成后：
- **左侧**：字幕烧录预览（视频模式）/ 音频播放器（音频模式）
- **右侧上**：点击下载 `.srt` 字幕文件
- **右侧下**：所有字幕文本预览

---

## 七、局域网共享（让同事也能用）

启动后查看自己的 IP：

```bash
# Windows
ipconfig

# Mac
ifconfig | grep "inet "
```

把 IP 发给同事，让他们在浏览器访问：

```
http://你的IP:7860
```

---

## 八、可选：GPU 加速

如果你有 **Nvidia 显卡**，安装 CUDA 版依赖后速度可提升 5–10 倍：

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

然后用文本编辑器打开 `app.py`，找到这一行：

```python
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
```

改为：

```python
model = WhisperModel("large-v3", device="cuda", compute_type="float16")
```

---

## 常见问题

**Q：点按钮没反应 / 一直转圈**
首次运行正在后台下载模型（3GB），等待即可，下载完会自动开始处理。

**Q：提示 `ffmpeg` 未找到**
重新安装 FFmpeg 后重启终端再运行。

**Q：TikTok / 抖音链接下载失败**
部分平台有防爬限制，可以先手动下载视频到本地，再用「上传视频」功能。

**Q：翻译结果中地名不准**
当前使用 Google 翻译，固有名词（如景点名）偶有偏差，属于正常现象。
