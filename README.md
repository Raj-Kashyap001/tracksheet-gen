# tracksheet-gen

Generate styled Excel tracksheets from job order CSV reports.

## Usage

```shell
# CLI
uv run gen_tracksheet.py 'Test Account.csv'

# GUI (requires GTK4 + libadwaita)
uv run gen_tracksheet_gui.py
```

## Output

Files are saved to `out/` as `[Account Name] [Date] [Shift] Tracksheet.xlsx`.

## Features

- Filters IN PROGRESS trips, sorts by Trip ID descending
- Auto-detects shift (A: 6am–2pm, B: 2pm–10pm, C: 10pm–6am)
- Unique color palette per account
- Trip Status formula auto-updates to COMPLETED when Remarks contains "trip end"
