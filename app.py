import sys
import time
import tempfile
import subprocess
import os
sys.stdout.reconfigure(encoding="utf-8")

import gradio as gr
import yt_dlp
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

model = None


def load_model():
    global model
    if model is None:
        print("加载模型中...")
        model = WhisperModel("large-v3", device="cpu", compute_type="int8")
        print("模型加载完成")
    return model


def fmt_srt(s):
    h, m = int(s // 3600), int((s % 3600) // 60)
    sec, ms = int(s % 60), int((s % 1) * 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"


def safe_translate(translator, text, retries=3):
    for _ in range(retries):
        try:
            return translator.translate(text)
        except Exception:
            time.sleep(1)
    return text


def download_video(url):
    """用 yt-dlp 下载视频到临时目录，返回文件路径"""
    tmp_dir = tempfile.mkdtemp()
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": os.path.join(tmp_dir, "video.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        ext = info.get("ext", "mp4")
    return os.path.join(tmp_dir, f"video.{ext}")


def burn_subtitles(video_path, srt_path):
    out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    out.close()
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles='{srt_escaped}'",
        "-c:a", "copy",
        out.name,
    ]
    subprocess.run(cmd, capture_output=True)
    return out.name


def transcribe_and_translate(video_path, progress, is_audio=False):
    m = load_model()
    translator = GoogleTranslator(source="ko", target="zh-CN")

    progress(0.3, desc="识别韩文中...")
    segments, _ = m.transcribe(video_path, language="ko", beam_size=5)
    segments = list(segments)

    if not segments:
        return None, None, None, "未识别到语音内容"

    progress(0.6, desc=f"翻译 {len(segments)} 段字幕...")
    srt_lines = []
    for i, seg in enumerate(segments):
        zh = safe_translate(translator, seg.text.strip())
        srt_lines.append(
            f"{i+1}\n{fmt_srt(seg.start)} --> {fmt_srt(seg.end)}\n{seg.text.strip()}\n{zh}\n"
        )
        progress(0.6 + 0.3 * (i + 1) / len(segments),
                 desc=f"翻译中 {i+1}/{len(segments)}")

    srt_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=".srt", mode="w", encoding="utf-8"
    )
    srt_file.write("\n".join(srt_lines))
    srt_file.close()

    preview_text = "\n".join(srt_lines)

    if is_audio:
        # 音频模式：返回音频播放器，不烧录视频
        return (
            gr.Video(visible=False),
            gr.Audio(value=video_path, visible=True),
            srt_file.name,
            f"完成！共 {len(segments)} 段字幕\n\n{preview_text}",
        )
    else:
        progress(0.92, desc="生成预览视频...")
        preview_video = burn_subtitles(video_path, srt_file.name)
        return (
            gr.Video(value=preview_video, visible=True),
            gr.Audio(visible=False),
            srt_file.name,
            f"完成！共 {len(segments)} 段字幕\n\n{preview_text}",
        )


def process_file(video_path, progress=gr.Progress()):
    if video_path is None:
        return None, None, None, "请先上传视频文件"
    progress(0.1, desc="加载模型...")
    return transcribe_and_translate(video_path, progress, is_audio=False)


def process_url(url, progress=gr.Progress()):
    if not url or not url.strip():
        return None, None, None, "请输入视频链接"
    progress(0.05, desc="下载视频中...")
    try:
        video_path = download_video(url.strip())
    except Exception as e:
        return None, None, None, f"下载失败：{e}"
    progress(0.2, desc="下载完成，加载模型...")
    return transcribe_and_translate(video_path, progress, is_audio=False)


def process_audio(audio_path, progress=gr.Progress()):
    if audio_path is None:
        return None, None, None, "请先上传音频文件"
    progress(0.1, desc="加载模型...")
    return transcribe_and_translate(audio_path, progress, is_audio=True)


# ── UI ──────────────────────────────────────────────────────────────
CSS = """
/* 全局字体 */
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }

/* 顶部 Banner */
#banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 8px;
    text-align: center;
    border: none;
}
#banner h1 {
    color: #ffffff;
    font-size: 28px;
    font-weight: 700;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}
#banner p {
    color: #a0aec0;
    font-size: 15px;
    margin: 0;
}

/* Tab 样式 */
.tab-nav button {
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 10px 24px !important;
    border-radius: 10px !important;
}
.tab-nav button.selected {
    background: #0f3460 !important;
    color: #ffffff !important;
}

/* 主按钮 */
#run-btn {
    background: linear-gradient(135deg, #0f3460, #533483) !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    height: 52px !important;
    color: white !important;
    margin-top: 8px;
    transition: opacity 0.2s;
}
#run-btn:hover { opacity: 0.85; }

/* 卡片容器 */
.gr-panel, .gr-box {
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
}

/* 输入框 */
textarea, input[type="text"] {
    border-radius: 10px !important;
    font-size: 14px !important;
}

/* 下载按钮区 */
#srt-download .wrap { border-radius: 12px !important; }

/* 字幕文本框 */
#subtitle-text textarea {
    font-family: "SF Mono", "Consolas", monospace !important;
    font-size: 13px !important;
    line-height: 1.7 !important;
    color: #2d3748 !important;
    background: #f8fafc !important;
}

/* 隐藏 Gradio 底部 footer */
footer { display: none !important; }
"""

with gr.Blocks(title="韩文字幕生成器", css=CSS) as demo:

    # Banner
    gr.HTML("""
    <div id="banner">
        <h1>🎬 韩文视频双语字幕生成器</h1>
        <p>支持视频链接 / 本地视频 / 音频文件 → 自动识别韩文 + 翻译为中文</p>
    </div>
    """)

    with gr.Tabs():
        with gr.Tab("🔗 粘贴链接"):
            url_input = gr.Textbox(
                label="视频链接",
                placeholder="粘贴 TikTok / YouTube / 抖音 / B站 等链接...",
                lines=1,
            )
            url_btn = gr.Button("下载并生成字幕", variant="primary", elem_id="run-btn")

        with gr.Tab("📁 上传视频"):
            file_input = gr.File(
                label="上传视频文件",
                file_types=[".mp4", ".mkv", ".avi", ".mov", ".webm"],
            )
            file_btn = gr.Button("开始生成字幕", variant="primary", elem_id="run-btn")

        with gr.Tab("🎵 上传音频"):
            audio_input = gr.File(
                label="上传音频文件",
                file_types=[".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"],
            )
            audio_btn = gr.Button("开始生成字幕", variant="primary", elem_id="run-btn")

    gr.HTML("<div style='height:12px'></div>")

    # 结果区
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            video_preview = gr.Video(label="字幕预览", interactive=False)
            audio_preview = gr.Audio(label="音频播放", interactive=False, visible=False)

        with gr.Column(scale=1):
            srt_output = gr.File(label="下载 SRT 字幕文件", elem_id="srt-download")
            log_output = gr.Textbox(
                label="字幕内容",
                lines=16,
                elem_id="subtitle-text",
                placeholder="字幕将在处理完成后显示在这里...",
            )

    url_btn.click(fn=process_url, inputs=url_input,
                  outputs=[video_preview, audio_preview, srt_output, log_output])
    file_btn.click(fn=process_file, inputs=file_input,
                   outputs=[video_preview, audio_preview, srt_output, log_output])
    audio_btn.click(fn=process_audio, inputs=audio_input,
                    outputs=[video_preview, audio_preview, srt_output, log_output])

if __name__ == "__main__":
    print("启动中...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False,
                theme=gr.themes.Soft(), inbrowser=True)
