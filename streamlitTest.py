import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from generateHtml import readData, generateSpansFromMultiSeq, generateSpansForHypSeq, getHtmlString, visComponents
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

metric_options = ['WDER', 'WER', 'TDER', 'F1']

class alignmentResult:
  def __init__(self, data:dict, speakerMapping:dict):
    self.speakerMapping = speakerMapping
    self.refSpeakers = data['ref']['speakers']
    self.refTokenNum = data['ref']['token-num']
    self.refSequences = data['ref']['sequences']
    
    self.hypSpeakers = data['hyp']['speakers']
    self.hypTokenNum = data['hyp']['token-num']
    self.hypSequence = data['hyp']['sequence']
  
  def getStats(self):
    pass
    
    
  def showStats(self):
    with st.sidebar:
      st.write("***Transcripts Information:***")
      with st.expander("**Reference**", expanded=True):
        # st.write("**Reference**")
        st.write("Token number: ", self.refTokenNum)
        st.write("speaker num: ", len(self.refSpeakers))
        st.write(str(self.refSpeakers))
        
      with st.expander("**Hypothesis**", expanded=True):
        # st.write("**Hypothesis**")
        st.write("Token number: ", self.hypTokenNum)
        st.write("speaker num: ", len(self.hypSpeakers))
        st.write(str(self.hypSpeakers))
    
      st.write("**Speaker Alignment**", self.speakerMapping)
    

def prepareDataForEval(refSequences, hypSequence):
  refAlignSequences = []
  for seq in refSequences:
    refAlignSequences.append([token['aligned-index'] for token in seq])
  
  hypSpeakerSequence = [token['speakerID'] for token in hypSequence]
  return refAlignSequences, hypSpeakerSequence


def displayMetric(selected_metrics, data):
  refSequences = data['ref']['sequences']
  hypSequence = data['hyp']['sequence']
  eval = Eval(hypTokens=hypSequence, refSequences=refSequences)
  if selected_metrics:
    for option in selected_metrics:
      if option == "WDER":
        wder = eval.WDER()
        st.metric(label="WDER", value="{:.2f}".format(wder))
      elif option == "WER":
        wer = eval.WER()
        st.metric(label="WER", value="{:.2f}".format(wer))
  

if __name__ == "__main__":
  st.set_page_config(layout="wide")
  
  # ==============
  with st.sidebar:
    uploaded_file = st.file_uploader("Upload the alignment result")
    
    default_selection = metric_options
    selected_metrics = st.sidebar.multiselect(
      "Evaluation Metric",
      metric_options,
      default=default_selection
    )
    
    align_speaker = st.sidebar.checkbox("Show Speaker Alignment")
    sd_err_highlight = st.sidebar.checkbox("Highlight diarization errors")
    asr_err_highlight = st.sidebar.checkbox("Highlight ASR errors")
  
  if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = json.loads(bytes_data)

    # refSequences = data['ref']['sequences']
    # hypSequence = data['hyp']['sequence']
    # refstr = generateSpansFromMultiSeq(refSequences)
    # hypstr = generateSpansForHypSeq(hypSequence)
    # eval = Eval(hypTokens=hypSequence, refSequences=refSequences)
    # speakerMapping = eval.speakerMapping
    # st.write(speakerMapping)
    # displayMetric(selected_metrics, data)
    # htmlStr = getHtmlString(refstr,hypstr)
    components = visComponents(data, selected_metrics)
    stats = alignmentResult(data, components.eval.speakerMapping)
    stats.showStats()
    htmlStr = components.getHtmlStr()
    with st.container():
      # path = Path(__file__).parent / "testTokens.html"
      # # st.components.v1.html(str(path))
      # file = open("testTokens.html")
      # st.components.v1.html(file.read(),height=720, scrolling=True)
      # file.close()
      st.components.v1.html(htmlStr,height=720, scrolling=True)