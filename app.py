import streamlit as st
import pandas as pd
import os
from datetime import datetime

DB = "jobs.csv"

STATUSES = [
    "Need to Apply",
    "Submitted",
    "Contact",
    "Rejected",
    "Lost Hope"
]

if os.path.exists(DB):
    df = pd.read_csv(DB)
else:
    df = pd.DataFrame(
        columns=["id", "text", "status", "created"]
    )


def save():
    df.to_csv(DB, index=False)


st.title("Job Tracker")

with st.form("add_job"):
    text = st.text_area(
        "Paste job link or job description"
    )

    submitted = st.form_submit_button("Add")

    if submitted and text.strip():

        new_row = {
            "id": len(df) + 1,
            "text": text.strip(),
            "status": "Need to Apply",
            "created": datetime.now()
        }

        df = pd.concat(
            [df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        df.to_csv(DB, index=False)

        st.rerun()

cols = st.columns(len(STATUSES))

for i, status in enumerate(STATUSES):

    with cols[i]:

        st.subheader(status)

        subset = df[df.status == status]

        for idx, row in subset.iterrows():

            with st.container(border=True):

                st.write(row["text"][:300])

                new_status = st.selectbox(
                    "Move to",
                    STATUSES,
                    index=STATUSES.index(status),
                    key=f"{row['id']}"
                )

                if new_status != status:

                    df.loc[idx, "status"] = new_status

                    save()

                    st.rerun()