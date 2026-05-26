import gradio as gr

from config import LOCAL_BACKEND, OPENAI_BACKEND
from services.elevenlabs_svc import LANG_LABEL_TO_CODE, VOICE_CHOICES, transcribe_elevenlabs, tts_elevenlabs
from services.workflows import process_auto, switch_backend, switch_source
from subtitle.align import process_merge_paste_and_upload
from subtitle.segment import process_segment
from ui.styles import CSS


with gr.Blocks(title="口播音频生成 Studio", css=CSS) as demo:
    gr.HTML("""
    <header class="app-hero">
        <div class="brand-lockup">
            <div class="brand-mark">▣</div>
            <div>
                <h1>口播音频生成 <span>Studio</span></h1>
                <p>视频链接 / 本地视频 / 音频文件 → 自动识别原文 → 翻译为中文 → 生成 SRT</p>
            </div>
        </div>
        <div class="hero-actions">
            <div class="status-pill"><i></i>就绪</div>
        </div>
    </header>
    """)

    with gr.Tabs(elem_classes=["main-tabs"]):

        # ── 生成字幕 Tab ──────────────────────────────
        with gr.Tab("生成字幕"):
            with gr.Row(equal_height=False, elem_classes=["studio-grid"]):
                with gr.Column(scale=2, elem_classes=["studio-card", "input-card"]):
                    gr.HTML("""
                    <div class="card-heading">
                        <div class="step-icon">✓</div>
                        <div>
                            <h2>1. 输入素材</h2>
                            <p>选择视频或音频素材，开始生成双语字幕</p>
                        </div>
                    </div>
                    """)
                    source_type = gr.Radio(
                        choices=["视频链接", "上传视频", "上传音频"],
                        value="视频链接",
                        show_label=False,
                        elem_classes=["source-switch"],
                    )
                    with gr.Column(visible=True) as url_group:
                        url_input = gr.Textbox(
                            show_label=False,
                            placeholder="粘贴 TikTok / YouTube / 抖音 / B站 视频链接...",
                            lines=1,
                        )
                    with gr.Column(visible=False) as video_group:
                        file_input = gr.File(
                            label="上传视频",
                            file_types=[".mp4", ".mkv", ".avi", ".mov", ".webm"],
                        )
                    with gr.Column(visible=False) as audio_group:
                        audio_input = gr.File(
                            label="上传音频",
                            file_types=[".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"],
                        )

                with gr.Column(scale=1, elem_classes=["studio-card", "action-card"]):
                    gr.HTML("""
                    <div class="card-heading compact">
                        <div class="step-icon bars">▮</div>
                        <div>
                            <h2>2. 模型选择</h2>
                        </div>
                    </div>
                    """)
                    backend_input = gr.Radio(
                        choices=[LOCAL_BACKEND, OPENAI_BACKEND],
                        value=LOCAL_BACKEND,
                        show_label=False,
                        elem_classes=["backend-switch"],
                    )
                    with gr.Group(visible=False, elem_classes=["api-key-panel"]) as api_key_group:
                        gr.HTML('<div class="field-title">OpenAI API Key</div>')
                        api_key_input = gr.Textbox(
                            show_label=False,
                            placeholder="填写 sk-...",
                            type="password",
                            lines=1,
                        )
                    gr.HTML('<div class="field-title">源语言</div>')
                    source_lang_input = gr.Dropdown(
                        choices=["自动检测", "韩文", "日文", "英文", "中文"],
                        value="自动检测",
                        show_label=False,
                    )

            with gr.Row(elem_classes=["action-bar-row"]):
                with gr.Column(elem_classes=["action-bar"]):
                    gen_btn = gr.Button("生成字幕", variant="primary", elem_id="run-btn")
                    gr.HTML('<span class="legal-note">请确保拥有视频的合法使用权</span>')

            gr.HTML('<div class="section-divider"><span>输出结果</span></div>')
            with gr.Row(equal_height=True, elem_classes=["result-grid"]):
                with gr.Column(scale=1, elem_classes=["studio-card"]):
                    video_preview = gr.Video(label="字幕预览", interactive=False)
                    audio_preview = gr.Audio(label="音频播放", interactive=False, visible=False)
                with gr.Column(scale=1, elem_classes=["studio-card"]):
                    with gr.Row(elem_classes=["downloads-row"]):
                        srt_output = gr.File(label="下载 SRT")
                        words_output = gr.File(label="下载词级 JSON")
                    log_output = gr.Textbox(
                        show_label=False,
                        lines=16,
                        elem_id="subtitle-text",
                        placeholder="字幕将在处理完成后显示在这里...",
                    )

        # ── 智能断句 Tab ──────────────────────────────
        with gr.Tab("智能断句"):
            gr.HTML("""
            <div class="page-title">
                <div class="step-icon bars">✂</div>
                <div class="page-title-text">
                    <span>Smart Segmentation</span>
                    <h2>智能断句与翻译</h2>
                    <p>输入一段长文本，AI 帮你按短视频字幕规则重新断句，并配上中文翻译。</p>
                </div>
            </div>
            """)
            with gr.Row(elem_classes=["studio-grid"]):
                with gr.Column(scale=2, elem_classes=["studio-card"]):
                    gr.HTML('<div class="field-title">原文</div>')
                    seg_input = gr.Textbox(
                        show_label=False,
                        lines=10,
                        placeholder="粘贴一整段需要断句的原文（韩文 / 日文 / 英文 等）...",
                    )
                with gr.Column(scale=1, elem_classes=["studio-card", "action-card"]):
                    gr.HTML('<div class="field-title">DeepSeek API Key</div>')
                    seg_api_key = gr.Textbox(
                        show_label=False,
                        placeholder="sk-...",
                        type="password",
                        lines=1,
                    )
                    seg_max_len = gr.Slider(
                        minimum=10, maximum=40, value=20, step=1,
                        label="每段最多字数",
                    )
                    seg_btn = gr.Button("AI 断句 + 翻译", variant="primary", elem_id="run-btn")
            with gr.Row(elem_classes=["result-grid"]):
                with gr.Column(scale=2, elem_classes=["studio-card"]):
                    gr.HTML('<div class="field-title">双语对照结果</div>')
                    seg_output = gr.Textbox(
                        show_label=False,
                        lines=16,
                        elem_id="subtitle-text",
                    )
                with gr.Column(scale=1, elem_classes=["studio-card"]):
                    gr.HTML('<div class="field-title">统计</div>')
                    seg_info = gr.Textbox(show_label=False, lines=1, interactive=False)

        # ── 口播音频生成 Tab ──────────────────────────
        with gr.Tab("口播音频生成"):
            gr.HTML("""
            <div class="page-title">
                <div class="step-icon bars">🎙</div>
                <div class="page-title-text">
                    <span>ElevenLabs Studio</span>
                    <h2>口播音频生成</h2>
                    <p>语音转文本 · 文本转语音，由 ElevenLabs 驱动</p>
                </div>
            </div>
            """)
            with gr.Row(elem_classes=["studio-grid"]):
                with gr.Column(scale=2, elem_classes=["studio-card"]):
                    gr.HTML('<div class="field-title">ElevenLabs API Key</div>')
                    el_api_key = gr.Textbox(
                        show_label=False,
                        placeholder="填写 sk_...",
                        type="password",
                        lines=1,
                    )

            with gr.Tabs():
                # ── 语音转文本 ──
                with gr.Tab("语音转文本"):
                    with gr.Row(equal_height=False, elem_classes=["studio-grid"]):
                        with gr.Column(scale=2, elem_classes=["studio-card", "input-card"]):
                            gr.HTML('<div class="field-title">上传音频 / 视频</div>')
                            el_stt_file = gr.File(
                                show_label=False,
                                file_types=[".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".mp4", ".mkv", ".mov"],
                            )
                        with gr.Column(scale=1, elem_classes=["studio-card", "action-card"]):
                            gr.HTML('<div class="field-title">语言</div>')
                            el_stt_lang = gr.Dropdown(
                                choices=list(LANG_LABEL_TO_CODE.keys()),
                                value="自动检测",
                                show_label=False,
                            )
                            el_stt_tag = gr.Checkbox(label="标注音频事件（笑声等）", value=True)
                            el_stt_diarize = gr.Checkbox(label="区分说话人", value=False)
                    with gr.Row(elem_classes=["action-bar-row"]):
                        with gr.Column(elem_classes=["action-bar"]):
                            el_stt_btn = gr.Button("开始转录", variant="primary", elem_id="run-btn")
                    gr.HTML('<div class="section-divider"><span>转录结果</span></div>')
                    with gr.Row(elem_classes=["result-grid"]):
                        with gr.Column(scale=2, elem_classes=["studio-card"]):
                            el_stt_text = gr.Textbox(
                                show_label=False,
                                lines=12,
                                elem_id="subtitle-text",
                                placeholder="转录完成后在这里显示...",
                            )
                        with gr.Column(scale=1, elem_classes=["studio-card"]):
                            el_stt_file_out = gr.File(label="下载 TXT")
                            el_stt_status = gr.Textbox(show_label=False, lines=1, interactive=False)

                # ── 文本转语音 ──
                with gr.Tab("文本转语音"):
                    with gr.Row(equal_height=False, elem_classes=["studio-grid"]):
                        with gr.Column(scale=2, elem_classes=["studio-card", "input-card"]):
                            gr.HTML('<div class="field-title">口播文案</div>')
                            el_tts_text = gr.Textbox(
                                show_label=False,
                                lines=8,
                                placeholder="输入要朗读的文本...",
                            )
                        with gr.Column(scale=1, elem_classes=["studio-card", "action-card"]):
                            gr.HTML('<div class="field-title">声音选择</div>')
                            el_tts_voice = gr.Dropdown(
                                choices=VOICE_CHOICES,
                                value="8jHHF8rMqMlg8if2mOUe",
                                show_label=False,
                            )
                            gr.HTML('<div class="field-title">模型</div>')
                            el_tts_model = gr.Dropdown(
                                choices=["eleven_v3", "eleven_turbo_v2_5", "eleven_multilingual_v2"],
                                value="eleven_v3",
                                show_label=False,
                            )
                    with gr.Row(elem_classes=["action-bar-row"]):
                        with gr.Column(elem_classes=["action-bar"]):
                            el_tts_btn = gr.Button("生成语音", variant="primary", elem_id="run-btn")
                    gr.HTML('<div class="section-divider"><span>生成结果</span></div>')
                    with gr.Row(elem_classes=["result-grid"]):
                        with gr.Column(scale=2, elem_classes=["studio-card"]):
                            el_tts_audio = gr.Audio(label="试听", interactive=False)
                        with gr.Column(scale=1, elem_classes=["studio-card"]):
                            el_tts_file_out = gr.File(label="下载 MP3")
                            el_tts_status = gr.Textbox(show_label=False, lines=1, interactive=False)

        # ── 合并 SRT Tab ──────────────────────────────
        with gr.Tab("合并 SRT"):
            gr.HTML("""
            <div class="page-title">
                <div class="step-icon">⚡</div>
                <div class="page-title-text">
                    <span>SRT Alignment</span>
                    <h2>合并字幕时间轴</h2>
                    <p>左侧粘贴 AI 重新断句后的双语文本（原文+中文交替），右侧上传词级时间戳 JSON，生成精确 SRT。</p>
                </div>
            </div>
            """)
            with gr.Row(elem_classes=["studio-grid"]):
                with gr.Column(scale=1, elem_classes=["studio-card"]):
                    gr.HTML('<div class="field-title">断句准确的双语文本</div>')
                    old_srt_text_input = gr.Textbox(
                        show_label=False,
                        lines=18,
                        placeholder="原文一行 + 中文一行，例如：\n비행기로 딱 한 시간 반.\n乘飞机正好一个半小时。\n칭다오 이박삼일 여행 코스 들어갑니다.\n开始青岛三天两夜旅行行程。",
                    )
                with gr.Column(scale=1, elem_classes=["studio-card"]):
                    gr.HTML('<div class="field-title">词级时间戳 JSON</div>')
                    words_json_input = gr.File(
                        label="上传 .words.json（生成字幕时同步导出）",
                        file_types=[".json"],
                    )
            with gr.Row(elem_classes=["action-bar-row"]):
                with gr.Column(elem_classes=["action-bar"]):
                    merge_btn = gr.Button("开始合并", variant="primary", elem_id="run-btn")

            with gr.Row(elem_classes=["result-grid"]):
                with gr.Column(scale=1, elem_classes=["studio-card"]):
                    merge_srt_output = gr.File(label="下载合并后的 SRT")
                with gr.Column(scale=1, elem_classes=["studio-card"]):
                    gr.HTML('<div class="field-title">合并结果预览</div>')
                    merge_log_output = gr.Textbox(
                        show_label=False,
                        lines=16,
                        elem_id="subtitle-text",
                        placeholder="合并完成后在这里预览...",
                    )

    # ── Event bindings ──────────────────────────────
    source_type.change(fn=switch_source, inputs=source_type, outputs=[url_group, video_group, audio_group])
    backend_input.change(fn=switch_backend, inputs=backend_input, outputs=api_key_group)
    gen_btn.click(
        fn=process_auto,
        inputs=[url_input, file_input, audio_input, backend_input, api_key_input, source_lang_input],
        outputs=[video_preview, audio_preview, srt_output, words_output, log_output],
    )
    merge_btn.click(fn=process_merge_paste_and_upload, inputs=[old_srt_text_input, words_json_input],
                    outputs=[merge_srt_output, merge_log_output])
    seg_btn.click(fn=process_segment, inputs=[seg_input, seg_max_len, seg_api_key],
                  outputs=[seg_output, seg_info])
    el_stt_btn.click(
        fn=transcribe_elevenlabs,
        inputs=[el_stt_file, el_api_key, el_stt_lang, el_stt_tag, el_stt_diarize],
        outputs=[el_stt_text, el_stt_file_out, el_stt_status],
    )
    el_tts_btn.click(
        fn=tts_elevenlabs,
        inputs=[el_tts_text, el_api_key, el_tts_voice, el_tts_model],
        outputs=[el_tts_audio, el_tts_file_out, el_tts_status],
    )
