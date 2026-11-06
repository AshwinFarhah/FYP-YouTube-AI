# NeuroShield AI - Setup Guide

NeuroShield AI is a local Chrome extension and FastAPI application that analyses YouTube videos using a trained Random Forest model, multimodal features, developmental scoring, and SHAP explanations. This guide assumes Windows PowerShell and that commands are run **from the project root** (the directory containing `requirements.txt`, `backend/`, and `models/`).

## 1. Prerequisites

- Python and pip (prefer a compatible Python version matching the project's pinned dependencies; this project was developed with Python 3.13).
- Google Chrome.
- FFmpeg, accessible as `ffmpeg` in PowerShell or via its full executable path.
- Node.js, available as `node` in PowerShell (the YouTube downloader explicitly requests the Node.js JavaScript runtime).
- Internet access to download public YouTube videos and any model/runtime assets not yet present locally.
- The supplied `models/` directory containing the trained `.joblib` model and associated JSON metadata.

Check installations:

```powershell
python --version
ffmpeg -version
node --version
```

If FFmpeg is not on PATH, find its executable with `where.exe ffmpeg` or locate `ffmpeg.exe` manually.

## 2. Create the Python environment

Open PowerShell in the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, use `.\.venv\Scripts\python.exe` instead of `python` in subsequent commands. Dependency installation may take time because audio and machine-learning packages are included.

## 3. Configure FFmpeg for this computer (required)

Open `modules/video_extractor.py`. Find:

```python
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
```

Replace the value with the **actual** full path on the your computer. For example:

```python
FFMPEG_PATH = r"C:\Users\EXAMINER\AppData\Local\Microsoft\WinGet\Packages\...\bin\ffmpeg.exe"
```

The above is only an example: do not paste it unchanged. Use the actual result from `where.exe ffmpeg`. Keep the `r` prefix and quotation marks. Confirm the file exists before starting analysis. Other tools may also use FFmpeg via PATH, so having FFmpeg on PATH is recommended.

## 4. Configure the encrypted analysis cache key (required)

**The backend will not start without `NEUROSHIELD_CACHE_KEY`.** This is a locally generated AES-256-GCM encryption key, **not** an OpenAI API key or paid external service credential.

For a fresh installation, generate a key in PowerShell:

```powershell
$env:NEUROSHIELD_CACHE_KEY = python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode())"
```

Keep this key securely if the same cached assessments need to be readable after restarting. On a later session, set the **same saved value**:

```powershell
$env:NEUROSHIELD_CACHE_KEY = "PASTE_YOUR_PREVIOUSLY_SAVED_KEY_HERE"
```

**Never commit or share the real key.** If you receive existing encrypted cache files, those files require the original encryption key; the newly generated key cannot decrypt them. The safest standalone demo package excludes previous cache files and allows you to generate a new key and fresh cache.

## 5. Start the backend

In the **same PowerShell window** where the cache key was set, and from the project root:

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

Keep this terminal open. Verify:

- `http://127.0.0.1:8000/model-status` — backend/model status
- `http://127.0.0.1:8000/docs` — FastAPI API documentation

If an import error appears, verify that you are in the project root and installed `requirements.txt` into the active environment.

## 6. Install the Chrome extension

1. Open `chrome://extensions` in Google Chrome.
2. Enable **Developer mode**.
3. Select **Load unpacked**.
4. Select the **`browser_extension/`** folder containing its `manifest.json` (do not select the project root).
5. Open a YouTube video and enable NeuroShield AI protection from the extension popup.
6. Wait for the assessment. Fresh analyses can take several minutes; subsequent cached assessments should be faster.

The extension expects the backend at `http://127.0.0.1:8000`. If the backend port is changed, update `BACKEND_URL` in the extension's `background.js` and reload the extension.

## 7. Suggested demonstration

1. Start the backend and verify `/model-status`.
2. Open a public YouTube video and turn on protection.
3. Wait for the model's risk result, developmental scores, hybrid assessment and SHAP explanation.
4. Refresh/revisit the same video to demonstrate cached retrieval.
5. Select **Reanalyse** to bypass the cache and run a new assessment. The interface should indicate reanalysis while the backend processes the video.
6. Confirm that a later normal request retrieves the latest cached assessment.

## 8. YouTube downloading and cookies

The downloader uses `yt-dlp`, Node.js, and optionally the root-level `yt-dlp.conf` and `cookies.txt`. Some YouTube videos may be blocked, require authentication, or be subject to rate limits; choose a publicly accessible video for demonstration. A cookies file is **not universally required**, and personal browser cookies must **not** be included in the submitted repository. The existing `yt-dlp.conf` references `cookies.txt`; if the file is not supplied, remove or comment out the `--cookies cookies.txt` line in that configuration, or provide a legitimate owned cookies file when necessary. Never share personal session cookies.

## 9. Troubleshooting

| Symptom | Check |
| --- | --- |
| Backend fails at startup with `NEUROSHIELD_CACHE_KEY` error | Set a valid base64-encoded 32-byte key in the **same** terminal before launching Uvicorn. |
| Cached result cannot be decrypted | Use the same key that encrypted it, or start with an empty cache for a new demo. Do not overwrite valuable encrypted caches. |
| FFmpeg not found | Correct `FFMPEG_PATH` in `modules/video_extractor.py`; check FFmpeg is installed. |
| Video download fails | Confirm internet access, Node.js, `yt-dlp` installation, public video access, and `yt-dlp.conf` / cookie settings. |
| Extension says backend unavailable | Confirm Uvicorn is running on port 8000; reload extension and YouTube tab. |
| Reanalyse returns cached result immediately | Inspect the `/analyze-video` request payload in the extension service worker Network tab; manual reanalysis must send `"force": true`. |
| New analysis takes a long time | Video download, audio transcription, feature extraction and explainability can take minutes. |

## 10. Project organisation and safe cleanup

Keep `backend/`, `browser_extension/`, `models/`, `modules/`, `utils/`, `data/`, and `results/` in their current positions unless code paths are updated and tested. Keep `requirements.txt`, `yt-dlp.conf`, and this README at the root. The downloader currently expects `cookies.txt` at the root if used. `urls.txt` can remain at the root until all research scripts that read it have been checked.

A new `research_scripts/` folder can hold the following **development-only** scripts after checking and updating their imports and relative paths:

- `analyse_dataset.py`
- `analyse_hybrid_agreement.py`
- `analyse_hybrid_framework.py`
- `analyse_hybrid_sensitivity.py`
- `analyse_hybrid_thresholds.py`
- `build_dataset.py`
- `explain_random_forest.py`
- `generate_explanation.py`
- `prepare_ml_dataset.py`
- `train_random_forest.py`

Do not move files inside `backend/`, `modules/`, or `browser_extension/` merely for appearance; Python imports and Chrome manifest paths depend on their locations. Exclude local IDE files (`.idea/`), virtual environments (`.venv/`), `__pycache__/`, downloaded temporary videos, personal cookies, and secrets from public repositories. Do not delete datasets, trained models, or results needed for project reproducibility.

## 11. Important security note

The project runs locally and requires no paid API key for Uvicorn, Random Forest or SHAP. It **does** require the cache encryption key described above. Do not include personal YouTube cookies, existing secret keys, or other credentials in your handoff or a public GitHub repository.
