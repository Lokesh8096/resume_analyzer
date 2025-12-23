import streamlit as st
import pandas as pd

from services.drive_loader import download_drive_file
from services.pdf_loader import extract_text_from_pdf
from services.resume_detector import is_image_based_resume
from services.analyzer import analyze_resume

from utils.csv_processor import process_dataframe
from utils.paste_processor import parse_pasted_data

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Resume Analyzer",
    layout="wide"
)

st.title("📄 Resume Skill & Grammar Analyzer")

# ---------------- LOAD PROMPT ----------------
with open("prompts/resume_analysis.txt", "r", encoding="utf-8") as f:
    PROMPT = f.read()

# ---------------- MODE SELECTION ----------------
mode = st.radio(
    "Select Mode",
    ["Single Resume", "Bulk Processing"],
    horizontal=True
)

# ======================================================
# 🟢 SINGLE RESUME MODE
# ======================================================
if mode == "Single Resume":
    st.subheader("🔍 Single Resume Analysis")

    name = st.text_input("Candidate Name")
    techstack = st.text_input("Expected Tech Stack (comma separated)")

    col1, col2 = st.columns(2)

    with col1:
        pdf = st.file_uploader("Upload Resume PDF", type=["pdf"])

    with col2:
        drive_link = st.text_input("Or Google Drive Resume Link")

    pasted_single = st.text_area(
        "Or paste one row from Excel / Sheets (Name<TAB>Techstack<TAB>DriveLink)",
        height=100,
        placeholder="John Doe\tMERN\thttps://drive.google.com/file/d/FILE_ID/view"
    )

    if st.button("Analyze Resume"):
        candidate_name = name.strip()
        candidate_tech = techstack.strip()
        drive_link_clean = drive_link.strip()

        # If no PDF or link provided, try to parse the pasted single row
        if not pdf and not drive_link_clean and pasted_single.strip():
            parsed_df = parse_pasted_data(pasted_single)
            valid_df = parsed_df[parsed_df["link_valid"] == True] if not parsed_df.empty else parsed_df
            if valid_df.empty:
                st.warning("No valid row found in pasted data")
                st.stop()
            row = valid_df.iloc[0]
            candidate_name = candidate_name or row.get("name", "")
            candidate_tech = candidate_tech or row.get("techstack", "")
            drive_link_clean = row.get("resume_link", "")

        if not candidate_tech:
            st.warning("Please enter expected tech stack (or include it in pasted row)")
            st.stop()

        if pdf:
            resume_text = extract_text_from_pdf(pdf)

        elif drive_link_clean:
            pdf_file = download_drive_file(drive_link_clean)
            resume_text = extract_text_from_pdf(pdf_file)

        else:
            st.warning("Upload a PDF, provide a Drive link, or paste a row with a valid Drive link")
            st.stop()

        if is_image_based_resume(resume_text):
            st.error("❌ Image-based resume detected. Text extraction not possible.")
        else:
            try:
                result = analyze_resume(
                    resume_text,
                    candidate_tech,
                    index=0,
                    prompt_template=PROMPT
                )
                st.success("✅ Analysis Complete")
                st.json(result)
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")

# ======================================================
# 🔵 BULK PROCESSING MODE
# ======================================================
elif mode == "Bulk Processing":
    st.subheader("📊 Bulk Resume Processing")

    tab1, tab2 = st.tabs(["📤 Upload CSV", "📋 Paste from Excel"])

    # --------------------------------------------------
    # 📤 CSV UPLOAD
    # --------------------------------------------------
    with tab1:
        st.markdown("**CSV Columns Required:** `name, techstack, resume_link`")

        csv_file = st.file_uploader("Upload CSV File", type=["csv"])

        if csv_file:
            df = pd.read_csv(csv_file)
            st.success(f"✅ {len(df)} records loaded")
            st.dataframe(df)

            if st.button("Analyze CSV Resumes"):
                with st.spinner("Analyzing resumes..."):
                    result_df = process_dataframe(df, PROMPT)

                st.success("✅ Bulk Analysis Completed")
                st.dataframe(result_df)

                st.download_button(
                    "⬇️ Download Results CSV",
                    result_df.to_csv(index=False),
                    "resume_analysis_results.csv"
                )

    # --------------------------------------------------
    # 📋 PASTE FROM EXCEL
    # --------------------------------------------------
    with tab2:
        st.markdown(
            """
            **Paste rows copied directly from Excel / Google Sheets**

            Format:
            ```
            Name    Techstack    DriveLink
            ```
            """
        )

        pasted_text = st.text_area(
            "Paste Excel Data Here",
            height=220,
            placeholder="Paste rows here (Ctrl+V)"
        )

        if st.button("Validate & Add to List"):
            df = parse_pasted_data(pasted_text)

            if df.empty:
                st.warning("⚠️ No valid rows detected")
            else:
                st.session_state["bulk_df"] = df
                st.success(f"✅ {len(df)} rows added")

        # ---------- SHOW VALIDATED LIST ----------
        if "bulk_df" in st.session_state:
            st.subheader("📋 Validated Resume List")

            st.dataframe(st.session_state["bulk_df"])

            invalid_df = st.session_state["bulk_df"][
                st.session_state["bulk_df"]["link_valid"] == False
            ]

            if not invalid_df.empty:
                st.error("❌ Invalid Drive Links Found")
                st.dataframe(invalid_df)

            # ---------- ANALYZE BUTTON ----------
            if st.button("Analyze All Valid Resumes"):
                valid_df = st.session_state["bulk_df"][
                    st.session_state["bulk_df"]["link_valid"] == True
                ]

                if valid_df.empty:
                    st.warning("No valid resumes to analyze")
                    st.stop()

                with st.spinner("Analyzing resumes..."):
                    result_df = process_dataframe(valid_df, PROMPT)

                st.success("✅ Bulk Analysis Completed")
                st.dataframe(result_df)

                st.download_button(
                    "⬇️ Download Results CSV",
                    result_df.to_csv(index=False),
                    "resume_analysis_results.csv"
                )
