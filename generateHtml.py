# from htbuilder import span, div, script, style, link, styles, HtmlElement, br
import json
from pathlib import Path
from eval import Eval

def readData(name):
  with open(name) as f:
    data = json.load(f)
  return data

def local_script(path):
    with open(path) as f:
        code = f.read()
    return "<script>" + code + "</script>"

def local_css(path):
  with open(path) as f:
    code = f.read()
  return "<style>"+code+"</style>"


def generateSpansFromMultiSeq(sequences):
  allTokens = getAllTokens(sequences)
  utterances = group_tokens_into_utterances(allTokens)
  html_string = ""
  for utt_id, utt in enumerate(utterances):
    speakerID = utt[0]["speakerID"]
    utt_div_Start = f'<div class="utterance-container" index="{utt_id}" speakerID="{speakerID}">\n <div class="inner-utterance" speakerID="{speakerID}">\n'
    utt_div_End = '</div>\n</div>\n'
    spans=[]
    speakerSpan = f'<span class="speaker" id="{speakerID}">{speakerID}: </span>'
    spans.append(speakerSpan)
    for token in utt:
      index = token['index']
      textVal = token['token']
      alignedIndex = token['aligned-index']
      alignedType = token["aligned-type"]
      speakerID = token["speakerID"]

      WDER_err, WER_err = checkTokenErrorType(token)
      span = f'<span class="ref" \
        index="{index}" \
          aligned-index="{alignedIndex}" \
            aligned-type="{alignedType}" \
              speakerID="{speakerID}" wder_err="{WDER_err}" wer_err="{WER_err}">\
                {textVal}\
                  </span>\n'
      spans.append(span)
    curr_utt_string = utt_div_Start + "".join(spans) + utt_div_End
    html_string = html_string + curr_utt_string
      
  return html_string

def generateSpansForHypSeq(sequence) -> str:
  utterances = group_tokens_into_utterances(sequence)
  html_string = ""
  for utt_id, utt in enumerate(utterances):
    speakerID = utt[0]["speakerID"]
    utt_div_Start = f'<div class="utterance-container" index="{utt_id}" speakerID="{speakerID}">\n <div class="inner-utterance" speakerID="{speakerID}">\n'
    utt_div_End = '</div>\n</div>\n'
    spans=[]
    speakerSpan = f'<span class="speaker" id="{speakerID}">{speakerID}: </span>'
    spans.append(speakerSpan)
    for token in utt:
      index = token['index']
      textVal = token['token']
      alignedType = token["aligned-type"]
      speakerID = token["speakerID"]
      WDER_err, WER_err = checkTokenErrorType(token)
      span = f'<span class="hyp" index="{index}" aligned-type="{alignedType}"\
        speakerID="{speakerID}" wder_err="{WDER_err}" wer_err="{WER_err}">\
          {textVal}</span>\n'
      spans.append(span)
    curr_utt_string = utt_div_Start + "".join(spans) + utt_div_End

    html_string = html_string + curr_utt_string
  return html_string

def checkTokenErrorType(token):
  WDER_err = "error" if 'WDER_err' in token else "not_error"
  WER_err = "not_error"
  if 'WER_err' in token:
    if token['WER_err'] == 'i':
      WER_err = 'insertion'
    elif token['WER_err'] == 'd':
      WER_err = 'deletion'
    elif token['WER_err'] == 's':
      WER_err = 'substitution'
  
  return WDER_err, WER_err

def getAllTokens(sequences):
  tokenList = []
  for i, seq in enumerate(sequences):
    for token in seq:
      tokenList.append(token)
  sortedTokens = sorted(tokenList, key=lambda x: x['index'])
  return sortedTokens

def getMetricHtmlStr(metrics, eval:Eval):

  htmlStart = '<ul class="metrics">\
    <li class="metric-title">Metrics:</li>'
  htmlEnd = '</ul>'
  for option in metrics:
    if option == "WDER":
      wder = eval.WDER()
      htmlStart += '<li id="WDER" class="selected metric">\
            <div class="metric-container WDER">\
            <div class="metric-name">WDER </div>\
              <div class="metric-value">{:.2f}</div>\
            </div>\
          </li>'.format(wder)
    elif option == "WER":
      wer = eval.WER()
      htmlStart += '<li id="WER" class="selected metric">\
                    <div class="metric-container WER">\
                    <div class="metric-name">WER </div>\
                   <div class="metric-value">{:.2f}</div>\
            </div>\
          </li>'.format(wer)
    elif option == "F1":
      f1, p, r = eval.F1()
      # print("precision:", p, "\n",  "recall:", r)
      # f1 = 0.79 # testing
      htmlStart += '<li id="F1" class="selected metric">\
              <div class="metric-container F1">\
              <div class="metric-name">F1 </div>\
              <div class="metric-value">{:.2f}</div>\
            </div>\
          </li>'.format(f1)
    elif option == "TDER":
      tder = eval.TDER()
      # tder = 0.43 # testing
      htmlStart += '<li id="TDER" class="selected metric">\
              <div class="metric-container TDER">\
              <div class="metric-name">TDER </div>\
              <div class="metric-value">{:.2f}</div>\
            </div>\
          </li>'.format(tder)
    elif option == "Precision":
      f1, p, r = eval.F1()
      # print("precision:", p, "\n",  "recall:", r)
      # f1 = 0.79 # testing
      htmlStart += '<li id="Precision" class="selected metric">\
              <div class="metric-container Precision">\
              <div class="metric-name">Precision </div>\
              <div class="metric-value">{:.2f}</div>\
            </div>\
          </li>'.format(p)
    elif option == "Recall":
      f1, p, r = eval.F1()
      # print("precision:", p, "\n",  "recall:", r)
      # f1 = 0.79 # testing
      htmlStart += '<li id="Recall" class="selected metric">\
              <div class="metric-container Recall">\
              <div class="metric-name">Recall </div>\
              <div class="metric-value">{:.2f}</div>\
            </div>\
          </li>'.format(r)    

  return htmlStart + htmlEnd

def htmlElements(metric, refstr, hypstr, speakerMapping: dict, annotation:str):
  ref = '<div class = "ref-container" id="ref">\n'+\
        '<div class= "ref-header"> Reference </div>' +\
    '<div class = "ref-text">' +\
      refstr + '</div>\n </div>\n'
  hyp = '<div class = "hyp-container" id="hyp">\n'+\
    '<div class= "hyp-header"> Hypothesis </div>' + \
    '<div class = "hyp-text">' +\
      hypstr + '</div>\n </div>\n'
  
  if annotation == 'None':
    annotation = ""
  annotationStr = '<div class="annotation_option" style="display:none;">' + annotation + '</div>'
  speakerMapping = '<div class="speaker-mapping" style="display:none;">' + json.dumps(speakerMapping) + '</div>'
  
  doc_container = '<div class="doc-container">'+ hyp + ref  + '</div>'
  body = ' <body>\n'+ speakerMapping + annotationStr + metric + doc_container + '</body>'
  # body = "<div id=\"hyp\">" + refstr + " </div><hr>" + "<div id=\"ref\">" + hypstr + "</div>\n"
  return [
    local_css(Path(__file__).parent / "src" / "transcriptvis.css"),
    body,
    local_script(Path(__file__).parent / "src" / "jquery-3.6.3.min.js"),
    local_script(Path(__file__).parent / "src" / "transcriptvis.js"),
  ]

def group_tokens_into_utterances(tokens) -> list:
    utterances = []
    current_utterance = []
    current_speaker = None
    for token in tokens:
        speaker = token['speakerID']
        if current_speaker is None:
            current_speaker = speaker
        elif current_speaker != speaker:
            utterances.append(current_utterance)
            current_utterance = []
            current_speaker = speaker
        current_utterance.append(token)
    utterances.append(current_utterance)
    # print(len(utterances))
    return utterances

class visComponents:
  def __init__(self, data, selectedMetrics:list = None, annotation_option:str = None) -> None:
    self.data = data
    self.eval = Eval(hypTokens=data['hyp']['sequence'], refSequences=data['ref']['sequences'])
    self.metrics = selectedMetrics
    self.annotation_option = annotation_option
  
  def getHtmlStr(self):
    speakerMapping = self.eval.speakerMapping
    metricStr = getMetricHtmlStr(self.metrics, self.eval)
    refstr = generateSpansFromMultiSeq(self.eval.refSequences)
    hypstr = generateSpansForHypSeq(self.eval.hypTokens)
    # htmlStr = getHtmlString(metricStr, refstr, hypstr, self.eval.speakerMapping)
    elements = htmlElements(metricStr, refstr, hypstr, self.eval.speakerMapping, self.annotation_option)
    htmlStr = ""
    for element in elements:
      htmlStr += element
    return htmlStr
  
  

def writeHtmlTest(refstr, hypstr):
  with open("testTokens.html", "w") as f:
    for element in htmlElements(refstr, hypstr):
      f.write(element)
    # f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>Test align words</title>\n<link rel=\"stylesheet\" href=\"src/transcriptvis.css\"><script src=\"src/jquery-3.6.3.min.js\">\
    #   </script><script src=\"src/transcriptvis.js\"></script>\n</head>\n<body>\n")
    
    # f.write("<div id=\"hyp\">")
    # f.write(hypstr)
    # f.write(" </div><hr>")
    # f.write("<div id=\"ref\">")
    # f.write(refstr)


    # f.write(" </div>\n</body>\n</html>")

if __name__ == "__main__":
  data = readData("mysample.json")
  # refSequences = data['ref']['sequences']
  # hypSequence = data['hyp']['sequence']

  selected_metrics = ['WER', "WDER"]
  components = visComponents(data, selected_metrics)
  htmlStr = components.getHtmlStr()
  with open("data/testTokens.html", "w") as f:
      f.write(htmlStr)