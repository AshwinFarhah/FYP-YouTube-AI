# ============================================================
# NeuroShield AI
# YouTube Video Downloader
# ============================================================

from pathlib import Path
import subprocess
import sys

# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TEMP_DIR = BASE_DIR / "backend" / "temp"

COOKIES_PATH = BASE_DIR / "cookies.txt"

YTDLP_CONFIG_PATH = BASE_DIR / "yt-dlp.conf"


TEMP_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DOWNLOAD YOUTUBE VIDEO
# ============================================================

def download_youtube_video(
    youtube_url: str
):

    print()
    print("=" * 60)
    print("NeuroShield AI - YouTube Download")
    print("=" * 60)

    print(
        "URL:",
        youtube_url
    )


    # --------------------------------------------------------
    # Output template
    # --------------------------------------------------------

    output_template = str(
        TEMP_DIR / "%(id)s.%(ext)s"
    )


    # --------------------------------------------------------
    # yt-dlp command
    # --------------------------------------------------------

    command = [
        sys.executable,
        "-m",
        "yt_dlp",

        "--no-playlist",

        "--merge-output-format",
        "mp4",

        "-f",
        "bv*+ba/b",

        "-o",
        output_template,
    ]


    # --------------------------------------------------------
    # Use existing yt-dlp configuration if available
    # --------------------------------------------------------

    if YTDLP_CONFIG_PATH.exists():

        command.extend([
            "--config-location",
            str(YTDLP_CONFIG_PATH)
        ])


    # --------------------------------------------------------
    # Use existing cookies if available
    # --------------------------------------------------------

    if COOKIES_PATH.exists():

        command.extend([
            "--cookies",
            str(COOKIES_PATH)
        ])


    command.append(
        youtube_url
    )


    print(
        "Downloading YouTube video..."
    )


    # --------------------------------------------------------
    # Run yt-dlp
    # --------------------------------------------------------

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        print(
            "YouTube download failed."
        )

        print(
            result.stderr[-2000:]
        )

        raise RuntimeError(
            "Could not download YouTube video."
        )


    # --------------------------------------------------------
    # Get video ID
    # --------------------------------------------------------

    id_command = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--get-id",
        "--no-playlist",
        youtube_url
    ]


    id_result = subprocess.run(
        id_command,
        capture_output=True,
        text=True
    )


    if id_result.returncode != 0:

        raise RuntimeError(
            "Could not determine YouTube video ID."
        )


    video_id = (
        id_result.stdout
        .strip()
        .splitlines()[0]
    )


    # --------------------------------------------------------
    # Locate downloaded file
    # --------------------------------------------------------

    possible_files = list(
        TEMP_DIR.glob(
            f"{video_id}.*"
        )
    )


    video_files = [
        file
        for file in possible_files
        if file.suffix.lower()
        in {
            ".mp4",
            ".mkv",
            ".webm"
        }
    ]


    if not video_files:

        raise RuntimeError(
            "Downloaded video file could not be located."
        )


    video_path = video_files[0]


    print(
        "YouTube video downloaded successfully."
    )

    print(
        "Video ID:",
        video_id
    )

    print(
        "Video path:",
        video_path
    )


    return {
        "video_id": video_id,
        "video_path": str(video_path)
    }