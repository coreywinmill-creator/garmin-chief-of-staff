# Garmin upgrade: history and recovery

This branch proposes changes for review before merging to main.

## Daily collection
- One scheduled run per UTC day at 23:00 UTC (6 PM EST / 7 PM EDT). GitHub Actions schedules are UTC and can be delayed.
- The collector requests up to four recent sleep days; the summary exports the latest valid record, retaining its actual date.
- Supported training readiness, training status, recovery time and VO2 max scalar fields are allowlisted where the installed client returns them. Missing fields remain missing; no values are inferred.
- Raw Garmin data stays on the ephemeral GitHub runner. Only the privacy-filtered summary is uploaded to the existing configured Drive file.

## Historical activities (separate manual operation)
1. The private, user-owned Drive JSON file `Garmin-History-Archive.json` is pre-created inside the historical archive folder.
2. The workflow uses its file ID to **update the same file in place**. Service accounts cannot create new files in personal My Drive because they have no storage quota.
3. The existing Garmin service account has Editor access to the archive file.
4. Open Actions → **Garmin history backfill (manual, privacy filtered)** → Run workflow.
5. Start with 365 days and 20 pages. Increase the bounds if needed. Each successful run replaces the previous archive, rather than creating dated versions.
6. The archive contains only allowlisted activity type, date, duration, distance, HR, calories, training load/effect and cadence. No activity IDs, coordinates, routes or account identifiers.
7. Backfill is bounded and may be incomplete if pagination is capped. Inspect the `truncated` field. This is not a historical sleep/HRV export.

## Testing and rollout
- Verify the daily workflow completes and its Drive report contains the expected sleep date, HRV and supported recovery fields.
- Run the manual backfill only after configuring the private Drive folder secret.
- This branch does not automatically connect archives to ChatGPT briefings. The Chief of Staff must read the Drive data when preparing a briefing.
- No secrets, raw reports or private health data should be committed to GitHub.
