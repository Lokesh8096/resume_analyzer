import pandas as pd
from services.drive_loader import download_drive_file
from services.pdf_loader import extract_text_from_pdf
from services.resume_detector import is_image_based_resume
from services.analyzer import analyze_resume


REQUIRED_COLUMNS = {"name", "techstack", "resume_link"}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Lowercase, strip, and replace spaces with underscores
    df = df.rename(columns=lambda c: c.strip().lower().replace(" ", "_"))
    return df


def _validate_columns(df: pd.DataFrame):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}. Expected: name, techstack, resume_link")


def process_dataframe(df, prompt):
    # Normalize and validate headers
    df = _normalize_columns(df)
    _validate_columns(df)

    results = []

    for i, row in df.iterrows():
        try:
            link = str(row["resume_link"]).strip()
            if not link or link.lower() == "nan":
                raise ValueError("Empty resume_link")

            pdf = download_drive_file(link)
            text = extract_text_from_pdf(pdf)

            if is_image_based_resume(text):
                results.append({
                    **row.to_dict(),
                    "status": "Image-based resume detected"
                })
                continue

            analysis = analyze_resume(
                text,
                str(row["techstack"]).strip(),
                i,
                prompt
            )

            # Flatten analysis dict into the row so it shows as table columns
            if isinstance(analysis, dict):
                results.append({**row.to_dict(), **analysis})
            else:
                results.append({**row.to_dict(), "error": "Unexpected analysis format", "raw_output": str(analysis)})

        except Exception as e:
            results.append({
                **row.to_dict(),
                "error": str(e)
            })

    return pd.DataFrame(results)
