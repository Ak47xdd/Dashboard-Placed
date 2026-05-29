# Supabase Backup Instructions (Contingency)

This folder contains backup instructions for two Supabase tables used by this project:

- `STUDENT_DATA`
- `CLASSIFICATION`

Backups are intended as a contingency measure, so you can restore data if anything goes wrong (accidental changes, corruption, or deployment issues).

---

## What to run

Run the utility script:

```bash
python form/backup.py
```

This script fetches all rows from both tables via Supabase REST and writes CSV files under `data/backups/`.

---

## Backup schedule

Perform a backup:

- **Every month**, _or_
- **Every 6 months** (if that better matches your operational needs)

Pick one cadence and stick to it.

---

## Backup log (run table)

Record each backup run in the tables below.

### Monthly backups

| Backup Date | Time (local) | Script Run              | `STUDENT_DATA.csv` created/updated | `CLASSIFICATION.csv` created/updated | Notes |
| ----------- | ------------ | ----------------------- | ---------------------------------- | ------------------------------------ | ----- |
| 28-05-2026  | 5:30PM       | `python form/backup.py` | YES                                | YES                                  | OK    |

### 6-month backups

| Backup Date | Time (local) | Script Run              | `STUDENT_DATA.csv` created/updated | `CLASSIFICATION.csv` created/updated | Notes |
| ----------- | ------------ | ----------------------- | ---------------------------------- | ------------------------------------ | ----- |
| 28-05-2026  | 5:30PM       | `python form/backup.py` | YES                                | YES                                  | OK    |

---

## Notes / best practices

- Use the same machine/environment where Supabase credentials are available (via `SUPABASE_URL` and `SUPABASE_KEY`).
- After running, confirm the script output shows success for **both** tables.
- If you want true “point-in-time” restoration, consider versioning the CSVs (e.g., saving timestamped copies) in addition to overwriting the latest files.
