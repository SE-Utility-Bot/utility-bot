from urllib.request import urlopen

import streamlit as st

st.markdown(
    urlopen(
        "https://raw.githubusercontent.com/PlaceReporter99/utility-bot/main/README.md"
    ).read().decode("utf-8"),
    unsafe_allow_html=True,
)
