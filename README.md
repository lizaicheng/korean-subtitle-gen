# 口播音频生成 Studio

上传视频 / 音频 / 粘贴链接，自动识别原文 → 翻译为中文 → 生成双语 SRT 字幕文件，并在浏览器中实时预览。

---

## 功能概览

| 功能 | 说明 |
|------|------|
| 🎬 生成字幕 | 视频链接 / 本地视频 / 音频 → 双语 SRT + 词级时间戳 JSON |
| ✂️ 智能断句 | 用 AI 将长句重新断成短视频字幕节奏，配中文翻译 |
| ⚡ 合并 SRT | 将 AI 重断的双语文本与词级时间戳精确对齐，生成新 SRT |

---

## 效果预览

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
2. 点击 **Download Python 3.x.x**
3. 安装时勾选 ✅ **Add Python to PATH**（重要！）

### Mac

```bash
brew install python
```

---

## 三、安装 FFmpeg

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
git clone https://github.com/lizaicheng/korean-subtitle-gen.git
cd korean-subtitle-gen
pip install faster-whisper deep-translator gradio yt-dlp openai
```

---

## 五、启动

```bash
python app.py
```

首次启动会自动下载 **Whisper large-v3 模型**（约 3GB），下载完成后缓存在本地，之后无需重复下载。

下载完成后浏览器会自动打开，或手动访问：

```
http://localhost:7860
```

暗色模式：

```
http://localhost:7860/?__theme=dark
```

---

## 六、使用方式

### 生成字幕

1. 选择输入来源：视频链接 / 上传视频 / 上传音频
2. 选择识别模型（本地免费 / OpenAI API）
3. 选择源语言（默认自动检测，也可指定韩文 / 日文 / 英文 / 中文）
4. 点击「生成字幕」
5. 生成完成后可下载：
   - `.srt` 双语字幕文件
   - `.words.json` 词级时间戳文件（供「合并 SRT」使用）

### 智能断句

当 Whisper 自动断句过长时，可用此功能重新断句：

1. 将生成的韩/日/英文原文粘贴进左侧文本框
2. 填入 DeepSeek API Key
3. 调整「每段最多字数」
4. 点击「AI 断句 + 翻译」，得到双语对照结果

### 合并 SRT

将 AI 重新断句后的文本与 Whisper 的精确时间戳合并：

1. 左侧粘贴「智能断句」的双语结果（原文一行 + 中文一行交替）
2. 右侧上传「生成字幕」时导出的 `.words.json`
3. 点击「开始合并」，得到精确时间轴的双语 SRT

---

## 七、可选：GPU 加速

### Windows（Nvidia 显卡）

安装 CUDA 版 PyTorch 后速度可提升 5–10 倍：

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

然后修改 `services/transcription.py`：

```python
# 将
model = WhisperModel(DEFAULT_WHISPER_MODEL, device="cpu", compute_type="int8")
# 改为
model = WhisperModel(DEFAULT_WHISPER_MODEL, device="cuda", compute_type="float16")
```

### Mac（Apple Silicon M1/M2/M3/M4）

faster-whisper 不支持 Apple MPS，推荐改用 `mlx-whisper`（Apple 官方优化，直接调用 M 系芯片 GPU，速度比 CPU 快 3–5 倍）：

```bash
pip install mlx-whisper
```

然后修改 `services/transcription.py`，将 `transcribe_local` 替换为：

```python
import mlx_whisper

def transcribe_local(media_path, language=None, initial_prompt=None):
    kwargs = {"path_or_hf_repo": "mlx-community/whisper-large-v3-mlx"}
    if language:
        kwargs["language"] = language
    if initial_prompt:
        kwargs["initial_prompt"] = initial_prompt
    result = mlx_whisper.transcribe(media_path, word_timestamps=True, **kwargs)
    out = []
    for seg in result.get("segments", []):
        words = [
            {"text": w["word"].strip(), "start": w["start"], "end": w["end"]}
            for w in seg.get("words", []) if w.get("word", "").strip()
        ]
        out.append({"start": seg["start"], "end": seg["end"], "text": seg["text"].strip(), "words": words})
    return out
```

### Intel Mac

无可用 GPU 加速路径，建议在界面中选择 **OpenAI API** 模式，云端处理速度更快。

---

## 八、局域网共享

```bash
# 查看本机 IP
ipconfig        # Windows
ifconfig | grep "inet "   # Mac
```

让同事访问：`http://你的IP:7860`

---

## 更新到最新版本

```bash
cd korean-subtitle-gen
git pull
pip install -r requirements.txt 2>/dev/null || true
```

---

## 常见问题

**Q：点按钮没反应 / 一直转圈**
首次运行正在后台下载模型（3GB），等待即可，下载完会自动开始处理。

**Q：提示 `ffmpeg` 未找到**
重新安装 FFmpeg 后重启终端再运行。

**Q：TikTok / 抖音链接下载失败**
部分平台有防爬限制，可以先手动下载视频到本地，再用「上传视频」功能。

**Q：识别结果有同音错字（如 임산부 识别成 인삼부）**
Whisper 对专有名词有时识别偏差，属正常现象。已开启 VAD 过滤和上下文断开来减少串联错误。后续可在代码中为 `transcribe_local` 传入 `initial_prompt` 参数提示关键词。

**Q：翻译结果中地名不准**
当前使用 Google 翻译，固有名词偶有偏差，属于正常现象。
