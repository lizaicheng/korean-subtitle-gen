import tempfile

from elevenlabs.client import ElevenLabs

LANG_LABEL_TO_CODE = {
    "自动检测": None,
    "英文": "eng",
    "中文": "zho",
    "韩文": "kor",
    "日文": "jpn",
}

VOICE_CHOICES = [
    ("Han - Conversational", "8jHHF8rMqMlg8if2mOUe"),
    ("韩国1", "Y5PTb4q9EX2NAl00Eg3W"),
    ("Mr. K - Korean Creator Voices", "Q3a15DhENXU8pKTHIccM"),
    ("Mr. K - Natural Korean Voice", "LKOcTG4J4tYTPR9DnLeM"),
    ("Hana Lee - Natural and Cheerful", "QPFsEL6IBxlT15xfiD6C"),
    ("Eun-joong - Deep & Calm Korean Narrator", "36g0LZWoT8jWnUnnCauK"),
    ("Jeong-Ah - Versatile Korean Female", "airYK6ydeWdrJg6gyZA3"),
]


def transcribe_elevenlabs(audio_path, api_key, language_label="自动检测", tag_audio_events=True, diarize=False):
    if not api_key or not api_key.strip():
        return "", None, "请填写 ElevenLabs API Key"
    if not audio_path:
        return "", None, "请上传音频或视频文件"

    lang_code = LANG_LABEL_TO_CODE.get(language_label)
    client = ElevenLabs(api_key=api_key.strip())

    with open(audio_path, "rb") as f:
        result = client.speech_to_text.convert(
            file=f,
            model_id="scribe_v2",
            tag_audio_events=tag_audio_events,
            language_code=lang_code,
            diarize=diarize,
        )

    text = result.text if hasattr(result, "text") else str(result)

    txt_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    txt_file.write(text)
    txt_file.close()

    return text, txt_file.name, "转录完成"


def tts_elevenlabs(text, api_key, voice_id, model_id="eleven_v3"):
    if not text or not text.strip():
        return None, None, "请输入文本"
    if not api_key or not api_key.strip():
        return None, None, "请填写 ElevenLabs API Key"
    if not voice_id or not voice_id.strip():
        return None, None, "请填写 Voice ID"

    client = ElevenLabs(api_key=api_key.strip())

    audio_iter = client.text_to_speech.convert(
        text=text.strip(),
        voice_id=voice_id.strip(),
        model_id=model_id,
        output_format="mp3_44100_128",
    )

    out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    for chunk in audio_iter:
        out.write(chunk)
    out.close()

    return out.name, out.name, "生成完成"
