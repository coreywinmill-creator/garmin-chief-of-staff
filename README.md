# Garmin Chief of Staff — cloud v2 compatibility test

Adapted from the user's **Garmin Comprehensive Upgrade Windows10** package. Unlike the earlier prototype, this runs its original `collector.py` and `build_summary.py` to produce **schema_version 2**, including sleep, seven-day steps/stress, 30-day activities, and optional HRV, Body Battery, readiness, VO2max, etc. *Only metrics supported by the installed Garmin library and available to the account will populate.* This has **not been tested against the user's Garmin account**.

## Important: test separately

**Do not use the ID of the working `Garmin-Chief-of-Staff-latest.json` file yet.** Create a separate blank JSON test file in your private Drive folder and grant a dedicated Google service account **Editor** access to that file. The service account must be able to access/update it; personal Drive restrictions can make this fail. Never share your health data publicly.

## Upload to private GitHub repository

Upload the **contents** of this ZIP to the root of `coreywinmill-creator/garmin-chief-of-staff`, preserving `.github/workflows/garmin-sync.yml`. On GitHub mobile, uploading folders can be awkward; GitHub desktop or web desktop mode is easier. Do not commit secrets or Garmin report files.

## Configure

1. In Google Cloud Console, enable the Google Drive API. Create a dedicated service account and JSON credential. Share **only the test file** with the service-account email as Editor. If the Google Drive file cannot be shared with a service account, this upload mechanism will need an OAuth user-authorization variant instead.
2. In GitHub repository **Settings → Secrets and variables → Actions**, create three repository secrets:
   - `GARMIN_PERSONAL_API_KEY` — the **Personal API key** your existing collector uses; **not** your Garmin login password. Do not paste it in chat.
   - `GOOGLE_SERVICE_ACCOUNT_JSON` — entire service-account JSON credential (never put this in a repository file).
   - `GARMIN_DRIVE_FILE_ID` — ID of the **test** JSON file, not the live file.
3. Enable Actions in the private repository if prompted. Go to **Actions → Garmin Chief of Staff cloud v2 test → Run workflow**.
4. Inspect the workflow result and test file. Compare the output with your existing schema v2 JSON and verify dates, metrics and activity count before any switch-over. Do not disable Windows collection until this is confirmed.

## Schedule and limitations

Scheduled daily at **09:00 UTC** (5 AM EDT / 4 AM EST), ahead of the 6:30 AM Eastern briefing, but GitHub schedules may be delayed or skipped. GitHub Actions and Google Cloud may have plan/usage costs. Garmin's Personal API client is unofficial; auth and optional method compatibility may change. Runners are ephemeral. Raw data is written only to temporary runner storage, not uploaded to GitHub or attached as workflow artifacts. The privacy-filtered summary excludes activity IDs, location coordinates, routes, profile and names. Existing collector may still produce empty optional metrics. GitHub secrets are sensitive and can be exposed to code with access to workflow execution; keep repository access tightly restricted.

This package is a **test deployment**, not a verified working cloud sync or a completed connection to ChatGPT scheduled briefs.
