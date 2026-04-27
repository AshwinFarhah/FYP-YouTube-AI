import subprocess
import time
import os

# =========================
# CONFIG
# =========================

OUTPUT_DIR = "data/videos"
SLEEP_BETWEEN_VIDEOS = 6      # prevents YouTube rate-limit
COOLDOWN_ON_FAIL = 20         # wait longer if blocked

# your dataset URLs (replace or load from file)
urls = [
    "https://www.youtube.com/watch?v=h4war7sLnuQ",
    "https://www.youtube.com/watch?v=wxMrtK-kYnE",
    "https://www.youtube.com/watch?v=fZ9WiuJPnNA",
    "https://www.youtube.com/watch?v=783EsrHchXA",
    "https://www.youtube.com/watch?v=yu44JRTIxSQ",
    "https://www.youtube.com/watch?v=3gt6cHooI6M",
    "https://www.youtube.com/watch?v=OeVp9S1HzqI",
    "https://www.youtube.com/watch?v=5015skRvqs8",
    "https://www.youtube.com/watch?v=vSYadh2xmcI",
]

# ensure output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# DOWNLOAD FUNCTION
# =========================

def download_video(url, index, total):
    print(f"\n⬇️ [{index}/{total}] Downloading: {url}")

    cmd = [
        "yt-dlp",
        "-f", "bv*+ba/b",
        "--merge-output-format", "mp4",
        "--sleep-interval", "3",
        "--max-sleep-interval", "8",
        "--retries", "10",
        "--concurrent-fragments", "1",
        "-o", f"{OUTPUT_DIR}/%(id)s.%(ext)s",
        url
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Success: {url}")
        return True

    except subprocess.CalledProcessError:
        print(f"❌ Failed: {url}")
        return False


# =========================
# MAIN LOOP
# =========================

print("🚀 Starting dataset download...\n")

success = 0
failed = 0

for i, url in enumerate(urls, start=1):

    ok = download_video(url, i, len(urls))

    if ok:
        success += 1
        time.sleep(SLEEP_BETWEEN_VIDEOS)
    else:
        failed += 1
        time.sleep(COOLDOWN_ON_FAIL)


# =========================
# SUMMARY
# =========================

print("\n========================")
print("📊 DOWNLOAD COMPLETE")
print("========================")
print(f"✅ Success: {success}")
print(f"❌ Failed: {failed}")
print("========================")