import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path




if __name__ == "__main__":
  st.set_page_config(layout="wide")
  with st.sidebar:
    uploaded_file = st.file_uploader("Choose a file")
    add_selectbox = st.sidebar.selectbox("Is this multi-speaker conversation?", ("yes", "no"))
