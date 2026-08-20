"""
===========================================================
VIDEO / AUDIO EXTRACTION MODULE

Multimodal Explainable AI Framework
YouTube Child Content Analysis

Purpose:
- Extract audio from videos
- Enforce the 300-second analysis limit
- Keep audio and visual analysis temporally aligned
- Store extracted audio inside the FYP project
===========================================================
"""

import os
import subprocess


# ============================================================
# CONFIGURATION
# ============================================================

MAX_AUDIO_SECONDS = 300

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

# Project-level extracted audio directory
AUDIO_OUTPUT_DIR = os.path.join(
    "Data",
    "Extracted",
    "Audio"
)

# Convert to absolute path
AUDIO_OUTPUT_DIR = os.path.abspath(
    AUDIO_OUTPUT_DIR
)

# Make sure directory exists
os.makedirs(
    AUDIO_OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# EXTRACT AUDIO
# ============================================================

def extract_audio(
        video_path,
        max_seconds=MAX_AUDIO_SECONDS
):
    """
    Extracts only the first max_seconds of audio.

    The extracted audio is stored in:

        Data/Extracted/Audio/

    This guarantees that the audio analysed by Librosa
    and Whisper corresponds to the same time window
    as the visual analysis.

    Returns:
        path to extracted WAV file
        or None if extraction fails
    """

    # --------------------------------------------------------
    # Validate video path
    # --------------------------------------------------------

    if video_path is None:

        print(
            "⚠️ Audio extraction skipped - no video path."
        )

        return None


    if not os.path.exists(video_path):

        print(
            "⚠️ Audio extraction skipped - video does not exist."
        )

        return None


    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    os.makedirs(
        AUDIO_OUTPUT_DIR,
        exist_ok=True
    )


    # --------------------------------------------------------
    # Create safe output filename
    # --------------------------------------------------------

    video_name = os.path.splitext(
        os.path.basename(video_path)
    )[0]


    output_filename = (
        video_name
        +
        "_300sec.wav"
    )


    output_path = os.path.join(
        AUDIO_OUTPUT_DIR,
        output_filename
    )


    # --------------------------------------------------------
    # Remove previous temporary/existing file
    # --------------------------------------------------------

    if os.path.exists(output_path):

        try:

            os.remove(
                output_path
            )

        except Exception as e:

            print(
                "⚠️ Could not remove existing audio file:",
                e
            )


    # ========================================================
    # FFMPEG COMMAND
    # ========================================================

    command = [

        FFMPEG_PATH,

        "-y",

        "-i",
        video_path,

        # Start from beginning
        "-ss",
        "0",

        # HARD 300-second limit
        "-t",
        str(max_seconds),

        # Convert to mono
        "-ac",
        "1",

        # Sample rate
        "-ar",
        "16000",

        # WAV PCM
        "-c:a",
        "pcm_s16le",

        output_path
    ]


    # ========================================================
    # RUN FFMPEG
    # ========================================================

    try:

        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True

        )

    except Exception as e:

        print(
            "❌ FFmpeg execution failed:",
            e
        )

        return None


    # ========================================================
    # VALIDATE OUTPUT
    # ========================================================

    if (
        result.returncode != 0
        or
        not os.path.exists(output_path)
    ):

        print(
            "⚠️ Audio extraction failed."
        )

        print(
            result.stderr[-1000:]
        )

        return None


    # --------------------------------------------------------
    # Check file size
    # --------------------------------------------------------

    if os.path.getsize(
        output_path
    ) == 0:

        print(
            "⚠️ Extracted audio file is empty."
        )

        try:

            os.remove(
                output_path
            )

        except Exception:

            pass

        return None


    # ========================================================
    # SUCCESS
    # ========================================================

    print(
        "   🎵 Audio extracted:",
        output_path
    )

    print(
        f"   ⏱️ Audio limit: "
        f"{max_seconds} seconds"
    )

    return output_path