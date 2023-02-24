import streamlit as st
from generateHtml import visComponents
import json
from eval import Eval


multi_select_theme =     """
    <style>
    span[data-baseweb="tag"] {
      background-color: #06d6a0 !important;
    }
    </style>
"""

metric_options = ['WDER', 'WER', 'TDER', 'F1', 'Precision', 'Recall']
annotation_options = ['Speaker Diarization Error (SD)', 'Speech Recognition Error (ASR)']
annotation_option_map = {
  'Speaker Diarization Error (SD)': 'SD',
  'Speech Recognition Error (ASR)' : 'ASR'
}

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
    st.markdown(multi_select_theme,unsafe_allow_html=True)
    default_selection = metric_options
    selected_metrics = st.sidebar.multiselect(
      "Evaluation Metric",
      metric_options,
      default=default_selection
    )
    
    # align_speaker = st.sidebar.checkbox("Show Speaker Alignment")
    # sd_err_highlight = st.sidebar.checkbox("Highlight diarization errors")
    # asr_err_highlight = st.sidebar.checkbox("Highlight ASR errors")

    selected_annotation = st.selectbox("Choose Annotation Type", annotation_options)
    annotationType = annotation_option_map[selected_annotation]
    
  if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = json.loads(bytes_data)

    components = visComponents(data, selected_metrics, annotationType)
    stats = alignmentResult(data, components.eval.speakerMapping)
    stats.showStats()
    htmlStr = components.getHtmlStr()
    # with st.container():
    st.components.v1.html(htmlStr,height=720, scrolling=True)