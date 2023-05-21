import numpy as np
from scipy import optimize #for speaker mapping

class Eval():
  def __init__(self, hypTokens:list, refSequences:list) -> None:
    self.hypTokens = hypTokens
    self.refSequences = refSequences
    self.hypSpeakers = list({token['speakerID'] for token in hypTokens if token['speakerID'] != '-'})
    self.hypSpeakerIndex = {spkID: i for i, spkID in enumerate(self.hypSpeakers)}
    self.refSpeakers = [seq[0]['speakerID'] for i, seq in enumerate(refSequences)]
    self.refSpeakerIndex = {spkID: i for i, spkID in enumerate(self.refSpeakers)}
    self.speakerMapping = self.get_speaker_mapping()
    self.set_ref_utterances()
    self.group_token_into_utterances()

    
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
  
  def set_ref_utterances(self):
    all_tokens = []
    for i, seq in enumerate(self.refSequences):
      for token in seq:
        all_tokens.append(token)
    self.sortedTokens = sorted(all_tokens, key=lambda x: x['index'])
    
  def group_token_into_utterances(self):
    """utterance here is different than generateHtml, we ignore gap tokens her
    """
    utterances = []
    current_utterance = []
    current_speaker = None
    for token in self.sortedTokens:
        speaker = token['speakerID']
        if token['token'] == '-':
          continue
        if current_speaker is None:
            current_speaker = speaker
        elif current_speaker != speaker:
            utterances.append(current_utterance)
            current_utterance = []
            current_speaker = speaker
        current_utterance.append(token)
    utterances.append(current_utterance)
    self.ref_utterances = utterances
    # print(len(self.ref_utterances))
  
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
        else:
          token['WDER_err'] = True
          self.hypTokens[aligned_index]['WDER_err'] = True # for testing, not wder err

    for i, token in enumerate(self.hypTokens): # for testing
      if token['aligned-type'] == 'gap':
        token['WDER_err'] = True
        continue
      # refToken = self.getHypTokenAlignedRefToken(token['index'])
      # if not refToken:
      #   token['WDER_err'] = True
      #   print("not find")
      # if self.speakerMapping[refToken['speakerID']] != token['speakerID']:
      #   token['WDER_err'] = True
      #   print("wrong speaker")
      #   print(self.hypTokens[i])
    return error_count/aligned_num
  
  def getHypTokenAlignedRefToken(self, hyp_index):
    for seq in self.refSequences:
      for token in seq:
        if token['aligned-index'] == hyp_index:
          return token
    return None
    
  def WER(self):
    # d, i, sub
    deletion, insertion, substitution = 0,0,0
    for i, token in enumerate(self.hypTokens):
      if token['token'] != '-' and token['aligned-type'] == 'gap':
        insertion += 1
        # token['WER_err'] = 'i'
        self.hypTokens[i]['WER_err'] = 'i'
        
    for seq in self.refSequences:
      for token in seq:
        if token['aligned-index'] == -1:
          deletion += 1
          token['WER_err'] = 'd'
        if token['aligned-type'] == 'partially match' or token['aligned-type'] == 'mismatch':
          substitution += 1
          token['WER_err'] = 's'
    # all_token_num = sum([len(seq) for seq in self.refSequences])
    all_token_num = 0
    for seq in self.refSequences:
      for token in seq:
        # print(token)
        if token['token'] != '-':
          all_token_num += 1
          
    # print("deletion: ", deletion)
    # print("insertion: ", insertion)
    # print("substitution: ", substitution)
    # print(all_token_num)
    # print((deletion+insertion+substitution)/all_token_num)
    return (deletion+insertion+substitution)/all_token_num
    

  def TDER(self):
    """_summary_
    """
    numerator, denominator = 0,0
    
    for utt in self.ref_utterances:
      length = len(utt)
      hyp_spks = set()
      ref_spk = utt[0]['speakerID']
      for token in utt:
        hypIndex = token['aligned-index']
        hypSpk = self.hypTokens[hypIndex]['speakerID']
        if hypSpk != '-':
          hyp_spks.add(hypSpk)
      
      alignedHypSpk = self.speakerMapping[ref_spk]
      if alignedHypSpk in hyp_spks:
        Ncorrect = 1
      else:
        Ncorrect = 0
      
      denominator += length
      numerator += length*(max(1, len(hyp_spks))-Ncorrect)
    return numerator/denominator
      
        
        

  def F1(self):
    """_summary_
    """
    # recall
    ref_token_count = 0
    correct_num = 0
    for seq in self.refSequences:
      for token in seq:
        if token['token'] == '-':
          continue
        ref_token_count += 1
        refSpk = token['speakerID']
        aligned_index = token['aligned-index']
        if aligned_index == -1:
          continue
        else:
          hypSpk = self.hypTokens[aligned_index]['speakerID']
          if self.speakerMapping[refSpk] == hypSpk:
            correct_num += 1
    recall = correct_num/ref_token_count
    
    # precision
    hyp_token_count = len(self.hypTokens)
    precision = correct_num/hyp_token_count
    # print(hyp_token_count)
    # print(ref_token_count)
    
    return 2*precision*recall/(precision+recall), precision, recall
      
  

if __name__ == "__main__":
  import json
  with open("sample.json") as f:
    data = json.load(f)
    refSequences = data['ref']['sequences']
    hypSequence = data['hyp']['sequence']
    
    eval = Eval( hypSequence, refSequences )
    eval.get_speaker_mapping()
    print(eval.WDER())


