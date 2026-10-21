"""Run from repository root: streamlit run app/streamlit_app.py."""
import json
import os
from pathlib import Path

import httpx
import streamlit as st

from churn_capstone.contracts import CONTRACT_VERSION, FeatureRow, SegmentProfile, read_table

st.set_page_config(page_title="Bank retention demo", layout="wide")
st.title("Customer retention workbench")
st.warning("Demo data and rule-based scores. These are not validated churn predictions.")
base_url = os.getenv("CHURN_API_URL", "http://127.0.0.1:8000").rstrip("/")
directory = Path(os.getenv("CHURN_ARTIFACT_DIR", "artifacts/demo"))
try:
    frame = read_table(directory / "features.csv", FeatureRow)
    profiles = read_table(directory / "segment_profiles.csv", SegmentProfile)
except (OSError, ValueError) as error:
    st.error(f"Demo artifacts unavailable. Run `churn demo` first. {error}")
    st.stop()

selected_id = st.selectbox("Customer", frame.customer_id.tolist())
selected = frame.loc[frame.customer_id == selected_id]
st.dataframe(selected, hide_index=True)
if st.button("Look up risk and segment"):
    try:
        response = httpx.post(f"{base_url}/predict", timeout=10, json={
            "contract_version": CONTRACT_VERSION, "customers": selected.to_dict("records"),
        })
        response.raise_for_status()
        prediction = response.json()["predictions"][0]
        st.metric("Demo risk score", f"{prediction['risk_score']:.3f}")
        profile = profiles.loc[profiles.segment_id == prediction["segment_id"]].iloc[0]
        st.write(profile.segment_name)
        st.caption(profile.description)
    except (httpx.HTTPError, KeyError, ValueError, IndexError) as error:
        st.error(f"Lookup unavailable. Check API health and matching artifact versions. {error}")
st.subheader("Segment profiles")
st.dataframe(profiles, hide_index=True)
st.subheader("Monitoring report")
try:
    st.json(json.loads((directory / "monitoring.json").read_text()))
except (OSError, ValueError):
    st.info("Monitoring report pending. Run `churn monitor` after predictions are available.")
