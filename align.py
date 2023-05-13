from align4d import align4d
import csv
import json
import argparse

def align_writeJson(ref: list[str], ref_speaker_label:list[str], hyp:list[str], hypo_speaker_label:list[str], output_name:str):
  """get alignment using align4d and parse the results to create a json file that contains all information for TranscribeView

  Args:
      ref (list[str]): a list of reference speech tokens
      ref_speaker_label (list[str]): the speaker labels for each reference token
      hyp (list[str]): a list of hypothesis speech tokens
      hypo_speaker_label (list[str]): speaker labels for each hyp tokens
      output_name (str): name of the output json file
  """
  align_result = align4d.align_with_auto_segment(hyp, ref, ref_speaker_label)
  hypTokens = align_result[0]
  alignedTokens = align_result[1:]
  alignedIndices = align4d.get_align_indices(align_result)
  originalIndices = align4d.get_ref_original_indices(ref, ref_speaker_label)
  alignedType = align4d.get_token_match_result(align_result)
  refSpeakers = align4d.get_unique_speaker_label(ref_speaker_label)
  hypSpeakerList = align4d.get_aligned_hypo_speaker_label(align_result, hypo_speaker_label)
  ref = refDict(alignedTokens, alignedIndices, originalIndices, alignedType, refSpeakers)
  hyp = hypDict(hypTokens, alignedType, hypSpeakerList)
  output = {}
  output['ref'] = ref
  output['hyp'] = hyp
  json_object = json.dumps(output, indent=4)
  with open(output_name, "w") as outfile:
    outfile.write(json_object)


def refDict(alignedTokenList:list[list[str]], 
            alignedIndexList:list[list[int]], 
            orginalIndexList:list[list[int]], 
            alignedType:list[str], 
            speakerList:list[str]
            ) -> dict:
  """create the dict for ref speeches

  Args:
      alignedTokenList (list[list[str]]): the aligned result for each speakers in ref speech, contains gap
      alignedIndexList (list[list[int]]): the hyp token index aligned by each ref result tokens
      orginalIndexList (list[list[int]]): the index of each aligned result token in the orignal transcript
      alignedType (list[str]): align, mismatch, or partially aligned
      speakerList (list[str]): speaker label ordered by their speech sequence in alginedTokenList

  Returns:
      dict: 
  """
  result = {}
  processedTokenList = []
  for seq in alignedTokenList:
    processedTokenList.append([token for token in seq if token != '-'])
  
  sequences = []
  speaker_set = set()
  tokenNum = 0
  for i, seq in enumerate(processedTokenList):
    curr_seq = []
    speakerID = speakerList[i]
    speaker_set.add(speakerID)
    for j, token in enumerate(seq):
      tokenInfo = {}
      tokenInfo['token'] = token
      tokenInfo['index'] = int(orginalIndexList[i][j])
      tokenInfo['aligned-index'] = int(alignedIndexList[i][j])
      tokenInfo['speakerID'] = speakerID
      if token != '-':
        tokenNum += 1
      if tokenInfo['aligned-index'] < 0:
        tokenInfo['aligned-type'] = 'gap'
      else:
        tokenInfo['aligned-type'] = alignedType[tokenInfo['aligned-index']]
      curr_seq.append(tokenInfo)
    sequences.append(curr_seq)
  
  result['speakers'] = list(speaker_set)
  result['sequences'] = sequences
  result['token-num'] = tokenNum
  return result


def hypDict(tokens:list[list[str]], alignedType:list[str], hypSpeakerList:list[str,int]) -> dict:
  """create the dict for hyp speeches

  Args:
      tokens (list[list[str]]): all hypothesis tokens contains gap
      alignedType (list[str]): align, mismatch, or partially aligned
      hypSpeakerList (list[str,int]): each tokens speaker information 

  Returns:
      dict: _description_
  """
  result = {}
  seq = []
  speaker_set = set()
  tokenNum = 0
  for i, token in enumerate(tokens):
    tokenInfo = {}
    tokenInfo['token'] = token
    tokenInfo['index'] = i
    tokenInfo['speakerID'] = hypSpeakerList[i]
    if hypSpeakerList[i] != '-':
      speaker_set.add(hypSpeakerList[i])
      tokenNum += 1
    # TODO: tokenInfo['alignedSpeaker']
    tokenInfo['aligned-type'] = alignedType[i]
    seq.append(tokenInfo)
  result['sequence'] = seq
  result['speakers'] = list(speaker_set)
  result['token-num'] = tokenNum
  return result

def readInput(name):
  try:
    with open(name) as f:
        csv_file = csv.reader(f)
        all_data = []
        for row in csv_file:
            if not row[-1]:
                all_data.append(row[0:-1])
            else:
                all_data.append(row)
            
        ref = all_data[0]
        ref_speaker_label = all_data[1]
        hyp = all_data[2]
        hyp_speaker_label = all_data[3]
        return ref, ref_speaker_label, hyp, hyp_speaker_label
  except:
    print("Input Error")


def test():
  path = "Bdb001_short_tokens.csv"
  # output = "rev_bdb001.csv"
  output = "test.json"
  with open(path) as f:
      csv_file = csv.reader(f)
      all_data = []
      for row in csv_file:
          if not row[-1]:
              all_data.append(row[0:-1])
          else:
              all_data.append(row)
          
      ref = all_data[0]
      ref_speaker_label = all_data[1]
      hyp = all_data[4]
      hyp_speaker_label = all_data[5]
      align_writeJson(ref, ref_speaker_label, hyp, hyp_speaker_label, output_name=output)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input_file', help='Input file path')
  # Parse the command line argumentss
  args = parser.parse_args()
  # Access the values of the arguments
  input_file = args.input_file
  if not input_file.endswith('.csv'):
    print("Input Type Error: please input .csv file")
    exit()

  output_name = input_file.split('.')[0] + ".json"

  ref, ref_speaker_label, hyp, hyp_speaker_label = readInput(input_file)
  align_writeJson(ref, ref_speaker_label, hyp, hyp_speaker_label, output_name)
  print(f'Alignment completed! \nOutput file: {output_name}')
  