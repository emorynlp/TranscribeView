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
    utt_div_Start = f'<div class="utterance" index="{utt_id}" speakerID="{speakerID}">\n'
    utt_div_End = '</div>\n'
    spans=[]
    speakerSpan = f'<span class="ref-speaker">{speakerID}: </span>'
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
    utt_div_Start = f'<div class="utterance" index="{utt_id}" speakerID="{speakerID}">\n'
    utt_div_End = '</div>\n'
    spans=[]
    speakerSpan = f'<span class="hyp-speaker">{speakerID}: </span>'
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
  return htmlStart + htmlEnd

def htmlElements(metric, refstr, hypstr):
  ref = '<div class = "ref-container" id="ref">\n'+\
        '<div class= "ref-header"> Reference </div>' +\
    '<div class = "ref-text">' +\
      refstr + '</div>\n </div>\n'
  hyp = '<div class = "hyp-container" id="hyp">\n'+\
    '<div class= "hyp-header"> Hypothesis </div>' + \
    '<div class = "hyp-text">' +\
      hypstr + '</div>\n </div>\n'
  
  doc_container = '<div class="doc-container">'+ hyp + ref  + '</div>'
  body = ' <body>\n'+  metric + doc_container + '</body>'
  # body = "<div id=\"hyp\">" + refstr + " </div><hr>" + "<div id=\"ref\">" + hypstr + "</div>\n"
  return [
    local_css(Path(__file__).parent / "src" / "transcriptvis.css"),
    body,
    local_script(Path(__file__).parent / "src" / "jquery-3.6.3.min.js"),
    local_script(Path(__file__).parent / "src" / "transcriptvis.js"),
  ]
  
def getHtmlString(metric, refstr, hypstr):
  resultStr = ""
  for element in htmlElements(metric, refstr, hypstr):
    resultStr += element
  return resultStr

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
  def __init__(self, data, selectedMetrics:list = None) -> None:
    self.data = data
    self.eval = Eval(hypTokens=data['hyp']['sequence'], refSequences=data['ref']['sequences'])
    self.metrics = selectedMetrics
  
  def getHtmlStr(self):
    metricStr = getMetricHtmlStr(self.metrics, self.eval)
    refstr = generateSpansFromMultiSeq(self.eval.refSequences)
    hypstr = generateSpansForHypSeq(self.eval.hypTokens)
    htmlStr = getHtmlString(metricStr, refstr,hypstr)
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
  data = readData("sample.json")
  # refSequences = data['ref']['sequences']
  # hypSequence = data['hyp']['sequence']

  selected_metrics = ['WER', "WDER"]
  components = visComponents(data, selected_metrics)
  htmlStr = components.getHtmlStr()
  with open("testTokens.html", "w") as f:
      f.write(htmlStr)