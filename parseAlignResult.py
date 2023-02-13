import json
import csv

'''
need json input file that has the alignment result
{
  'ref': {
    'speakers': {A,B,C},
    'utterances': {
      {start:0, end:1, speaker:A}
    },
    'sequences': {
      'A': {
        'tokens': {
          {token: 'Hello',
           index: 0,
           algined-index: 2,
           aligned-type: ('gap','missmatch','matched')
          },
          {
            token: 'How',....
          }
        }
      }
      'B': {
        ...
      }
    }
  },
  'hyp': {
    'speakers': {0,1,2,3},
    'tokens': {
      {
        token: 'Yeah',
        index: 0,
        aligned-speaker: A,
        ...
      }
    }
  }
  
}
'''

def readcsv(path):
  """read aligned result csv file

  Args:
      path : string filename to the csv result

  Returns:
      list: returns the list of rows from csv file, 
  """
  with open(path) as f:
    csv_file = csv.reader(f)
    all_data = []
    for row in csv_file:
      if not row[-1]:
        all_data.append(row[0:-1])
      else:
        all_data.append(row)
      
    return all_data

def refDict(alignedTokenList:list[list[str]], alignedIndexList:list[list[int]], orginalIndexList:list[list[int]], alignedType:list[str], speakerList:list[str]):
  result = {}
  processedTokenList = []
  for seq in alignedTokenList:
    processedTokenList.append([token for token in seq if token != '-'])
  
  sequences = []
  for i, seq in enumerate(processedTokenList):
    seqDict = {}
    curr_seq = []
    speakerID = speakerList[i]
    for j, token in enumerate(seq):
      tokenInfo = {}
      tokenInfo['token'] = token
      tokenInfo['index'] = int(orginalIndexList[i][j])
      tokenInfo['aligned-index'] = int(alignedIndexList[i][j])
      tokenInfo['speakerID'] = speakerID
      if tokenInfo['aligned-index'] < 0:
        tokenInfo['aligned-type'] = 'gap'
      else:
        tokenInfo['aligned-type'] = alignedType[tokenInfo['aligned-index']]
      curr_seq.append(tokenInfo)
    # TODO: use speaker id
    sequences.append(curr_seq)
  
  result['sequences'] = sequences
  return result

def hypDict(tokens:list[list[str]], alignedType:list[str], hypSpeakerList:list[str,int]):
  result = {}
  seq = []
  for i, token in enumerate(tokens):
    tokenInfo = {}
    tokenInfo['token'] = token
    tokenInfo['index'] = i
    tokenInfo['speakerID'] = hypSpeakerList[i]
    # TODO: tokenInfo['alignedSpeaker']
    tokenInfo['aligned-type'] = alignedType[i]
    seq.append(tokenInfo)
  result['sequence'] = seq
  return result

def writeJson(name):
  all_data = readcsv("example_output.csv")
  hypTokens = all_data[0]
  alignedTokens, alignedIndices, orignalIndices, alignedType = all_data[1:4], all_data[5:8], all_data[8:11], all_data[4]
  refSpeakers, hypSpeakerList = all_data[11], all_data[12]
  ref = refDict(alignedTokens, alignedIndices, orignalIndices, alignedType, refSpeakers)
  hyp = hypDict(hypTokens, alignedType, hypSpeakerList)
  output = {}
  output['ref'] = ref
  output['hyp'] = hyp
  json_object = json.dumps(output, indent=4)
  with open("sample.json", "w") as outfile:
    outfile.write(json_object)
  
  
def test():
  all_data = readcsv("example_output.csv")
  alignedTokens, alignedIndices, orignalIndices, alignedType = all_data[1:4], all_data[5:8], all_data[8:11], all_data[4]
  
  refDict(alignedTokens, alignedIndices, orignalIndices, alignedType)


if __name__ == "__main__":
  writeJson("example_output.csv")