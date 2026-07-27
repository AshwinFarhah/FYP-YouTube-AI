import os
import whisper
import traceback

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"


model = whisper.load_model("base")


def extract_transcript(audio_path):

    try:

        result = model.transcribe(
            audio_path,
            fp16=False
        )

        return result["text"].strip()


    except Exception:

        traceback.print_exc()

        return ""