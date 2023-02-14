import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from generateHtml import readData, generateSpansFromMultiSeq, generateSpansForHypSeq, getHtmlString
import json
from eval import Eval
# DATE_COLUMN = 'date/time'
# DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
#             'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

# @st.cache
# def load_data(nrows):
#     data = pd.read_csv(DATA_URL, nrows=nrows)
#     lowercase = lambda x: str(x).lower()
#     data.rename(lowercase, axis='columns', inplace=True)
#     data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
#     return data
  
# col1, col2 = st.columns((3, 3))
# filename = col1.selectbox(label="File:", options=["1","2"])


# data_load_state = st.text('Loading data...')
# data = load_data(10000)
# data_load_state.text("Done! (using st.cache)")

# if st.checkbox('Show raw data'):
#     st.subheader('Raw data')
#     st.write(data)

# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

# with col2:
#   # Some number in the range 0-23
#   hour_to_filter = st.slider('hour', 0, 23, 17)
#   filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

#   st.subheader('Map of all pickups at %s:00' % hour_to_filter)
#   st.map(filtered_data)

# with col1:

metric_options = ['DER', 'WDER', 'WER', 'TDER', 'F1']

def prepareDataForEval(refSequences, hypSequence):
  refAlignSequences = []
  for seq in refSequences:
    refAlignSequences.append([token['aligned-index'] for token in seq])
  
  hypSpeakerSequence = [token['speakerID'] for token in hypSequence]
  return refAlignSequences, hypSpeakerSequence

if __name__ == "__main__":
  st.set_page_config(layout="wide")
  with st.sidebar:
    uploaded_file = st.file_uploader("Upload the alignment result")
      
    add_selectbox = st.sidebar.selectbox("Is this multi-speaker conversation?", ("yes", "no"))
    selected_metrics = st.sidebar.multiselect(
      "Evaluation Metric",
      metric_options
    )
    err_highlight = st.sidebar.checkbox("Highlight errors")
  
  if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = json.loads(bytes_data)
    refSequences = data['ref']['sequences']
    hypSequence = data['hyp']['sequence']
    refstr = generateSpansFromMultiSeq(refSequences)
    hypstr = generateSpansForHypSeq(hypSequence)
    eval = Eval(hypTokens=hypSequence, refSequences=refSequences)
    wder = eval.WDER()
    st.metric(label="WDER", value="{:.2f}".format(wder))
    htmlStr = getHtmlString(refstr,hypstr)
    with st.container():
      # path = Path(__file__).parent / "testTokens.html"
      # # st.components.v1.html(str(path))
      # file = open("testTokens.html")
      # st.components.v1.html(file.read(),height=720, scrolling=True)
      # file.close()
      st.components.v1.html(htmlStr,height=720, scrolling=True)