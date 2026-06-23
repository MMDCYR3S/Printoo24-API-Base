#!/usr/bin/env python3
"""
Kurdish Translation Script
Reads translation mappings from Excel and replaces Persian text with Kurdish in source files.
Place this script next to the Excel file inside the src folder (or adjust BASE_DIR below).
"""

import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime

EXCEL_FILE = "printoo24_kurdish_translations.xlsx"

# Base directory: parent of "src" folder
# Since script is placed inside src/, go one level up
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent  # parent of src/

LOG_FILE = SCRIPT_DIR / "translation_log.txt"


def run():
    excel_path = SCRIPT_DIR / EXCEL_FILE
    if not excel_path.exists():
        print(f"[ERROR] Excel file not found: {excel_path}")
        sys.exit(1)

    df = pd.read_excel(excel_path)
    df.columns = [c.strip() for c in df.columns]

    success_entries = []
    failed_entries = []

    for idx, row in df.iterrows():
        file_rel = str(row["File Address"]).strip()
        line_num = int(row["Line"])
        persian = str(row["Persian Text"]).strip()
        kurdish = str(row["Kurdish Text (Sorani)"]).strip()

        file_path = BASE_DIR / file_rel

        if not file_path.exists():
            failed_entries.append({
                "row": idx + 2,
                "file": file_rel,
                "line": line_num,
                "persian": persian,
                "reason": "File not found"
            })
            print(f"[SKIP] Row {idx+2}: File not found → {file_rel}")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # line_num is 1-based
        target_idx = line_num - 1
        if target_idx >= len(lines):
            failed_entries.append({
                "row": idx + 2,
                "file": file_rel,
                "line": line_num,
                "persian": persian,
                "reason": f"File has only {len(lines)} lines"
            })
            print(f"[SKIP] Row {idx+2}: Line {line_num} out of range in {file_rel}")
            continue

        original_line = lines[target_idx]
        if persian not in original_line:
            failed_entries.append({
                "row": idx + 2,
                "file": file_rel,
                "line": line_num,
                "persian": persian,
                "reason": "Persian text not found on specified line"
            })
            print(f"[SKIP] Row {idx+2}: Persian text not found on line {line_num} of {file_rel}")
            print(f"         Expected : {persian!r}")
            print(f"         Found    : {original_line.rstrip()!r}")
            continue

        new_line = original_line.replace(persian, kurdish, 1)
        lines[target_idx] = new_line

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        success_entries.append({
            "row": idx + 2,
            "file": file_rel,
            "line": line_num,
            "persian": persian,
            "kurdish": kurdish
        })
        print(f"[OK]   Row {idx+2}: {file_rel}:{line_num}")

    # Write log file
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write(f"Kurdish Translation Log — {now}\n")
        log.write("=" * 60 + "\n\n")

        log.write(f"✅ SUCCESSFUL ({len(success_entries)} items)\n")
        log.write("-" * 40 + "\n")
        for e in success_entries:
            log.write(f"  Row {e['row']}: {e['file']}:{e['line']}\n")
            log.write(f"    FA: {e['persian']}\n")
            log.write(f"    KU: {e['kurdish']}\n\n")

        log.write(f"\n❌ FAILED ({len(failed_entries)} items)\n")
        log.write("-" * 40 + "\n")
        for e in failed_entries:
            log.write(f"  Row {e['row']}: {e['file']}:{e['line']}\n")
            log.write(f"    Reason : {e['reason']}\n")
            log.write(f"    Persian: {e['persian']}\n\n")

    print("\n" + "=" * 50)
    print(f"Done. ✅ {len(success_entries)} succeeded | ❌ {len(failed_entries)} failed")
    print(f"Log saved to: {LOG_FILE}")


if __name__ == "__main__":
    run()
