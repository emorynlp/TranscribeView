import numpy as np
from scipy import optimize
# evaluation script
# included metrics: WDER, JER, Text-DER(utterance level), WER

# neede more information:
# the original speaker id for hypothesis and ground-truth sequences

# (token, spk_id)
# Input to alignment tool: 
#        2 lists of tokens [hi, long, time, no, see], [Hi, long, no, see]
#        2 lists of speaker ids and utterance segments [(1,15,A), (16,50,B) ....], [(1,13,spk_0), ...]
#        Same for ground-truth and hypothesis transcripts

# output from alignment tool:
#         align each ground truth sequence to hypothesis transcripts
#         1. one csv recording all words and gaps? (need speaker information for each sequence)
#         2. [A-1, A-2, A-3, B-1, B-2, 0, 0, -1, C-1, C-2]
#             0: gap, (-1: missmatch ?) do we need it?
#         3. each speaker a list of alignment to target sequence, and a list of target sequence's id
#            [1,2,3,5,0,-1,10...], [6,7,8,9,...], [15,30,31,31,...], [spk_0,spk_0,spk_1,spk_1, ....]

class Eval():
  def __init__(self, hypTokens:list, refSequences:list) -> None:
    self.hypTokens = hypTokens
    self.refSequences = refSequences
    self.hypSpeakers = list({token['speakerID'] for token in hypTokens if token['speakerID'] != '-'})
    self.hypSpeakerIndex = {spkID: i for i, spkID in enumerate(self.hypSpeakers)}
    self.refSpeakers = [seq[0]['speakerID'] for i, seq in enumerate(refSequences)]
    self.refSpeakerIndex = {spkID: i for i, spkID in enumerate(self.refSpeakers)}
    self.speakerMapping = self.get_speaker_mapping()
    
  def get_speaker_mapping(self):
    cost_matrix = self.build_cost_matrix()
    row_index, col_index = optimize.linear_sum_assignment(-cost_matrix) # linear_sum_assignment wants the minimum cost, here we want the largest
    refSpkIDs = self.inverse_mapping(self.refSpeakerIndex)
    hypSpkIDs = self.inverse_mapping(self.hypSpeakerIndex)
    speaker_alignment = {refSpkIDs[ref_index]:hypSpkIDs[hyp_index] for ref_index, hyp_index in enumerate(col_index)}
    # print(speaker_alignment)
    return speaker_alignment

  def inverse_mapping(self, mapping):
    return {value: key for key, value in mapping.items()}

  def build_cost_matrix(self):
    """Build the (m x n) cost matrix for linear sum assignment to match speakers
    m is the number of reference speakers, n is the number of hypothesis speakers
    each entry[i,j], stores the number of aligned tokens between ref speaker i and hyp speaker j
    """
    cost_matrix = np.zeros((len(self.refSpeakers), len(self.hypSpeakers)))
    for i, refTokens in enumerate(self.refSequences):
      for hypSpk in self.hypSpeakers:
        hyp_indices_for_curr_spk = [token['index'] for (index, token) in enumerate(self.hypTokens) if token["speakerID"] == hypSpk]
        ref_aligned_indices_for_curr_spk = [token['aligned-index'] for token in refTokens]
        cost_matrix[i, self.hypSpeakerIndex[hypSpk]] += len(set(ref_aligned_indices_for_curr_spk) & set(hyp_indices_for_curr_spk))
    return cost_matrix
  
  def WDER(self):
    """Word diarization error rate:
    WDER = (Sis + Cis)/(S+C) 
    the error rate amoung aligned tokens (not including gaps)
    """
    error_count = 0
    aligned_num = 0
    for seq in self.refSequences:
      for token in seq:
        refSpk = token['speakerID']
        aligned_index = token['aligned-index']
        if aligned_index >= 0 and self.hypTokens[aligned_index]['speakerID']!="-":
          aligned_num += 1
          hypSpk = self.hypTokens[aligned_index]['speakerID']
          if self.speakerMapping[refSpk] != hypSpk:
            self.hypTokens[aligned_index]['WDER_err'] = True # record WDER error
            token['WDER_err'] = True
            error_count += 1

    return error_count/aligned_num
    
  def WER(self):
    # d, i, sub
    deletion, insertion, substitution = 0,0,0
    for token in self.hypTokens:
      if token['token'] != '-' and token['aligned-type'] == 'gap':
        insertion += 1
        token['WER_err'] = 'i'
        
    for seq in self.refSequences:
      for token in seq:
        if token['aligned-index'] == -1:
          deletion += 1
          token['WER_err'] = 'd'
        if token['aligned-type'] == 'partially match' or token['aligned-type'] == 'mismatch':
          substitution += 1
          token['WER_err'] = 's'
    all_token_num = sum([len(seq) for seq in self.refSequences])
    return (deletion+insertion+substitution)/all_token_num
    





def WJER(hyp_spk_labels, ref_spks_alignments):
  """Word-level Jaccard error rate

  Args:
      hyp_spk_labels (_type_): _description_
      ref_spks_alignments (_type_): _description_
  """
  pass

  

if __name__ == "__main__":
  import json
  with open("sample.json") as f:
    data = json.load(f)
    refSequences = data['ref']['sequences']
    hypSequence = data['hyp']['sequence']
    
    eval = Eval( hypSequence, refSequences )
    eval.get_speaker_mapping()
    print(eval.WDER())


