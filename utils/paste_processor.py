import re
import pandas as pd

DRIVE_REGEX = r"https://drive\.google\.com/"

def parse_pasted_data(raw_text: str):
    rows = []
    lines = raw_text.strip().split("\n")

    for line in lines:
        parts = line.split("\t")
        if len(parts) < 3:
            continue

        name, techstack, link = parts[0].strip(), parts[1].strip(), parts[2].strip()

        is_valid_link = bool(re.search(DRIVE_REGEX, link))

        rows.append({
            "name": name,
            "techstack": techstack,
            "resume_link": link,
            "link_valid": is_valid_link
        })

    return pd.DataFrame(rows)
