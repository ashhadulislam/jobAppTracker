import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime
DB = "jobs.csv"
STATUSES = [
    "Need to Apply",
    "Submitted",
    "Contact",
    "Rejected",
    "Lost Hope"
]

# -----------------------------
# Helpers
# -----------------------------
def load_data():
    if os.path.exists(DB):
        return pd.read_csv(DB)
    return pd.DataFrame(
        columns=[
            "id",
            "status",
            "text",
            "url",
            "notes",
            "created_at",
            "updated_at",
        ]
    )

def save_data(df):
    df.to_csv(DB, index=False)

def extract_url(text):
    urls = re.findall(r"https?://\S+", text)
    return urls[0] if urls else ""

# -----------------------------
# Load Data
# -----------------------------
df = load_data()
st.set_page_config(
    page_title="Job Tracker",
    layout="wide"
)
st.title("📋 Job Tracker")
st.info(
    """
    ⚠️ Streamlit Community Cloud storage is temporary.
    Download a backup periodically.
    If the app resets, upload your CSV backup and continue where you left off.
    """
)
# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Data")
    uploaded_file = st.file_uploader(
        "Restore from CSV",
        type=["csv"]
    )
    if uploaded_file is not None:
        restored_df = pd.read_csv(uploaded_file)
        save_data(restored_df)
        st.success("Data restored")
        st.rerun()
    st.divider()
    st.metric(
        "Jobs Tracked",
        len(df)
    )
    st.download_button(
        label="⬇️ Download CSV Backup",
        data=df.to_csv(index=False),
        file_name="job_tracker_backup.csv",
        mime="text/csv"
    )
    st.download_button(
        label="⬇️ Download JSON Backup",
        data=json.dumps(
            df.to_dict("records"),
            indent=2,
            default=str
        ),
        file_name="job_tracker_backup.json",
        mime="application/json"
    )
# -----------------------------
# Add Job
# -----------------------------
st.subheader("Add Job")
with st.form("add_job"):
    text = st.text_area(
        "Paste job link or description"
    )
    notes = st.text_area(
        "Notes (optional)"
    )
    submitted = st.form_submit_button(
        "Add Job"
    )
    if submitted and text.strip():
        now = datetime.now().isoformat()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_id = 1
        if len(df):
            next_id = int(df["id"].max()) + 1
        new_row = {
            "id": next_id,
            "status": "Need to Apply",
            "text": text.strip(),
            "url": extract_url(text),
            "notes": notes,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        df = pd.concat(
            [df, pd.DataFrame([new_row])],
            ignore_index=True
        )
        save_data(df)
        st.success("Job added")
        st.rerun()
st.divider()

st.subheader("Summary")
summary_cols = st.columns(len(STATUSES))
for i, status in enumerate(STATUSES):
    summary_cols[i].metric(
        status,
        len(df[df.status == status])
    )

# -----------------------------
# Job Pipeline
# -----------------------------
st.header("Application Pipeline")
for status in STATUSES:
    subset = df[df.status == status]
    count = len(subset)
    default_open = status in [
        "Need to Apply",
        "Submitted",
        "Contact"
    ]
    with st.expander(
        f"{status} ({count})",
        expanded=default_open
    ):
        if len(subset) == 0:
            st.caption("No jobs")
            continue
        for idx, row in subset.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([8, 2])
                with col1:
                    st.markdown(
                        f"### #{int(row['id'])}"
                    )
                    st.write(row["text"])
                    if str(row["url"]).strip():
                        st.link_button(
                            "🔗 Open Link",
                            row["url"]
                        )
                    if str(row["notes"]).strip():
                        st.info(
                            f"📝 {row['notes']}"
                        )
                    st.caption(
                        f"Created: {row['created_at']}"
                    )
                    st.caption(
                        f"Updated: {row['updated_at']}"
                    )
                with col2:
                    move_to = st.selectbox(
                        "Status",
                        STATUSES,
                        index=STATUSES.index(status),
                        key=f"move_{row['id']}"
                    )
                    if move_to != status:
                        df.loc[idx, "status"] = move_to
                        df.loc[idx, "updated_at"] = (
                            datetime.now()
                            .strftime("%Y-%m-%d %H:%M:%S")
                        )
                        save_data(df)
                        st.rerun()
                    if st.button(
                        "🗑 Delete",
                        key=f"delete_{row['id']}"
                    ):
                        df = df[df["id"] != row["id"]]
                        save_data(df)
                        st.rerun()