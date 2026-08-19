import os
import whisper
import traceback


# =====================================================
# FFMPEG
# =====================================================

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"


# =====================================================
# LOAD WHISPER MODEL
# =====================================================

model = whisper.load_model(
    "base"
)


# =====================================================
# TRANSCRIPT EXTRACTION
# =====================================================

def extract_transcript(audio_path):

    # -------------------------------------------------
    # No audio
    # -------------------------------------------------

    if audio_path is None:

        print(
            "⚠️ Whisper skipped - no audio."
        )

        return ""

    # -------------------------------------------------
    # Check file exists
    # -------------------------------------------------

    if not os.path.exists(audio_path):

        print(
            "⚠️ Whisper skipped - audio file does not exist."
        )

        return ""

    # -------------------------------------------------
    # Whisper
    # -------------------------------------------------

    try:

        result = model.transcribe(
            audio_path,
            fp16=False
        )

        return result.get(
            "text",
            ""
        ).strip()

    except Exception:

        print(
            "❌ Whisper transcription failed."
        )

        traceback.print_exc()

        return ""