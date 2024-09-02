# ICS to Text and CSV Converter

A Python script to process `.ics` calendar files, merge events, remove duplicates, and filter based on keywords. Output results in both text and CSV formats.

## Setup

```bash
python -m venv venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Default (processes `samples` directory with predefined keywords):

```bash
python ics2text.py
```

Custom folder and keywords:

```bash
python ics2text.py /path/to/ics/folder keyword1 keyword2 keyword3
```

- `/path/to/ics/folder`: Folder containing `.ics` files.
- `keyword1 keyword2 keyword3`: Keywords to filter events (OR query).

## Output

- `merged_filtered_events.txt`: Text format of filtered events.
- `merged_filtered_events.csv`: CSV format with columns: Start, End, Guest number, Event title or summary, Location, Guests (newline-separated).
