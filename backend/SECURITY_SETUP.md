# NeuroShield AI — AES-256-GCM cache encryption

## Installation
From the project root, install `cryptography` in your existing Python virtual environment:

```powershell
python -m pip install cryptography
```

Copy the updated `app.py` and new `cache_crypto.py` into your existing project. Keep all other project files unchanged.

## Key generation (PowerShell)
Generate a random 256-bit key locally and set it for the *current terminal session*:

```powershell
$env:NEUROSHIELD_CACHE_KEY = python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode())"
```

**Important:** Keep this key in a password manager or securely configured secret store *before* closing the terminal. Do not commit the key, place it in the extension, or include it in the report. A new key on every restart will make previously encrypted cache files unreadable. To reuse the key, set `$env:NEUROSHIELD_CACHE_KEY` to the **same** saved value in each terminal session.

Start Uvicorn from the same terminal:

```powershell
uvicorn backend.app:app --reload
```

The backend intentionally refuses to start without a valid key. The `cryptography` package must be installed.

## Existing cache migration
Existing `backend/cache/<video_id>.json` plaintext analysis results are encrypted automatically **on first successful cache access**. Untouched legacy cache files remain plaintext until accessed. Back up the cache before deployment, and plan an offline bulk migration if you need all existing cache files encrypted immediately. Do not delete old cache files without checking whether they are needed.

Encrypted cache envelopes contain `format`, `nonce`, and `ciphertext`. The 12-byte nonce is random per write. The YouTube video ID is authenticated as associated data, preventing ciphertext swapping between cache files. GCM authentication rejects tampering and incorrect keys.

**Note:** The cache filename still contains the video ID; encryption does not hide which video IDs were analyzed, file sizes, access patterns, runtime memory, or logs. Backend communication over the public internet still requires HTTPS/TLS.

## Final combined testing (after all changes)
1. Backend starts with the correct key and fails to start with a missing/invalid key.
2. New analysis writes an encrypted JSON envelope (no plaintext features or SHAP values).
3. Repeating the same URL returns a complete cached result.
4. A legacy plaintext cache migrates to encrypted format on access.
5. Corrupting ciphertext or changing the key fails authentication; original file remains intact.
6. Existing API URL validation, request validation, concurrency, job cleanup and safe errors remain correct.
7. Fresh video analysis still completes: feature extraction → Random Forest → developmental scoring → hybrid assessment → SHAP.
8. Chrome extension popup, overlay, settings, light/dark themes and notification flows still work.
9. For any remote deployment, verify HTTPS and restrict CORS/origin exposure appropriately.

The supplied ZIP does not include runtime cache files, model artifacts or your deployment configuration, so those cannot be validated from the archive alone.
