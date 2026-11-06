
# ============================================================
# NeuroShield AI - PERF-01
# Fresh Video Analysis Processing Time
# ============================================================

import time
import requests

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://127.0.0.1:8000"

# Use a video that has NOT been analysed before.
VIDEO_URL = "https://www.youtube.com/watch?v=06JVSGqbHdE"

POLL_INTERVAL = 2
MAX_WAIT_SECONDS = 1200


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print()
    print("=" * 65)
    print("                NeuroShield AI - PERF-01")
    print("           Fresh Video Analysis Processing Time")
    print("=" * 65)

    # --------------------------------------------------------
    # STEP 1: Validate YouTube URL
    # --------------------------------------------------------

    if not VIDEO_URL.startswith(
        (
            "https://www.youtube.com/watch?v=",
            "https://youtu.be/"
        )
    ):
        print("\nERROR: Please enter a valid YouTube URL.")
        print("Test Status: NOT TESTED")
        return

    print("\nVideo URL:", VIDEO_URL)
    print("Submitting analysis request...")

    # --------------------------------------------------------
    # STEP 2: Start performance timer
    # --------------------------------------------------------

    start_time = time.perf_counter()

    response = requests.post(
        f"{BASE_URL}/analyze-video",
        json={"youtube_url": VIDEO_URL},
        timeout=30
    )

    response.raise_for_status()

    job_data = response.json()
    job_id = job_data["job_id"]

    print("Job ID:", job_id)
    print("Waiting for analysis completion...")

    # --------------------------------------------------------
    # STEP 3: Poll backend until analysis completes
    # --------------------------------------------------------

    attempts = 0
    result = None
    final_status = "timeout"
    error_message = None

    while time.perf_counter() - start_time < MAX_WAIT_SECONDS:

        response = requests.get(
            f"{BASE_URL}/analysis-status/{job_id}",
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        attempts += 1

        status = str(
            data.get("status", "")
        ).lower()

        if status in ("complete", "completed"):

            final_status = status
            result = data.get("result", {})
            break

        if status in ("failed", "error"):

            final_status = status
            error_message = data.get(
                "error",
                "Unknown backend error"
            )
            break

        time.sleep(POLL_INTERVAL)

    # --------------------------------------------------------
    # STEP 4: Stop performance timer
    # --------------------------------------------------------

    elapsed = time.perf_counter() - start_time

    # --------------------------------------------------------
    # STEP 5: Identify analysis source
    # --------------------------------------------------------

    if isinstance(result, dict):

        analysis_source = result.get(
            "analysis_source",
            "Not reported"
        )

    else:

        analysis_source = "Not available"

    # --------------------------------------------------------
    # STEP 6: Display performance results
    # --------------------------------------------------------

    print()
    print("-" * 65)
    print("PERFORMANCE RESULTS")
    print("-" * 65)

    print(f"Job Status       : {final_status}")
    print(f"Analysis Source  : {analysis_source}")
    print(f"Elapsed Time     : {elapsed:.2f} seconds")
    print(f"Elapsed Minutes  : {elapsed / 60:.2f} minutes")
    print(f"Polling Attempts : {attempts}")
    print(f"Polling Interval : {POLL_INTERVAL} seconds")

    if error_message:
        print(f"Backend Error    : {error_message}")

    # --------------------------------------------------------
    # STEP 7: Validate results
    # --------------------------------------------------------

    completed = final_status in (
        "complete",
        "completed"
    )

    fresh = str(analysis_source).lower() in (
        "live",
        "fresh"
    )

    print()
    print("-" * 65)
    print("VALIDATION RESULTS")
    print("-" * 65)

    print(
        "Analysis Completed :",
        "PASS" if completed else "FAIL"
    )

    print(
        "Fresh Analysis     :",
        "PASS" if fresh else "NOT CONFIRMED"
    )

    # --------------------------------------------------------
    # STEP 8: Determine overall test status
    # --------------------------------------------------------

    if completed and fresh:

        test_status = "PASS"

    elif completed and not fresh:

        test_status = "NOT VERIFIED (possibly cached)"

    else:

        test_status = "FAIL"

    print()
    print("Test Status        :", test_status)

    print("=" * 65)
    print()


# ============================================================
# RUN TEST
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except requests.exceptions.ConnectionError:

        print()
        print("ERROR: Cannot connect to NeuroShield AI backend.")
        print("Make sure FastAPI is running.")
        print("Test Status: FAIL")

    except requests.exceptions.Timeout:

        print()
        print("ERROR: Backend request timed out.")
        print("Test Status: FAIL")

    except requests.exceptions.RequestException as error:

        print()
        print("Request Error:", error)
        print("Test Status: FAIL")

    except (KeyError, ValueError, TypeError) as error:

        print()
        print("Unexpected Response Error:", error)
        print("Test Status: FAIL")
