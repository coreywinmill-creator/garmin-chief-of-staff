# Garmin upgrade: history and recovery

This branch proposes changes for review before merging to main.

## Daily collection
- One scheduled run per UTC day at 23:00 UTC (6 PM EST / 7 PM EDT). GitHub Actions schedules are UTC and can be delayed.
- The collector requests up to four recent sleep days; the summary exports the latest valid record, retaining its actual date.
- Supported training readiness, training status, recovery time and VO2 max scalar fields are allowlisted where the installed client returns them. Missing fields remain missing; no values are inferred.
- Raw Garmin data stays on the ephemeral GitHub runner. Only the privacy-filtered summary is uploaded to the existing configured Drive file.

## Historical activities (separate manual operation)
1. Create a **private** Google Drive folder for Garmin activity archives. Grant the existing Google service account Editor access to that folder.
2. Add the folder ID as the GitHub Actions repository secret `GARMIN_HISTORY_DRIVE_FOLDER_ID`. Never place credentials or health records in this public repository.
3. After merging, open Actions → **Garmin history backfill (manual, privacy filtered)** → Run workflow.
4. Start with 365 days and 20 pages. Inspect the output archive. Increase to 3650 days / 100 pages if necessary.
5. The backfill uploads a dated, sanitized JSON archive to the private folder; it does not overwrite the existing daily summary. It includes only activity type, date, duration, distance, HR, calories, training load/effect and cadence. No activity IDs, coordinates, routes or account identifiers.
6. Backfill is bounded, may be incomplete if pagination is capped, and depends on Garmin API availability. Inspect the `truncated` field. It is not a complete export of all historical sleep/HRV; that requires a separate validated endpoint and storage plan.

## Testing and rollout
- Verify the daily workflow completes and its Drive report contains the expected sleep date, HRV and supported recovery fields.
- Run the manual backfill only after configuring the private Drive folder secret.
- This branch does not automatically connect archives to ChatGPT briefings. The Chief of Staff must read the Drive data when preparing a briefing.
- No secrets, raw reports or private health data should be committed to GitHub.
