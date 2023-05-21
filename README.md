# TranscribeView
TranscribeView is a web-based tool designed to evaluate and visualize errors in speech recognition and speaker
diarization. It provides an interface for assessing both speaker recognition and speaker diarization errors. The system
leverages the 'align4d' package, a powerful multiple sequence alignment tool, to accurately map reference and hypothesis
transcripts. By combining these features, TranscribeView aims to aid in the advancement of data-driven conversational AI research.


## Installation
```shell
git clone https://github.com/emorynlp/TranscribeView.git
cd TranscribeView
pip install --upgrade pip
pip install -r requirements.txt
```

## Getting Started
Using TranscribeView involves two main steps: Running the alignment script and then feeding the generated JSON file into
the TranscribeView system. Here's a step-by-step guide on how to do that:

### 1. Prepare your transcripts
Your transcripts need to be in a specific format for TranscribeView to process them. Prepare a CSV file with four rows:
```
hmm,You,can,tell,if,it,picking,up
C,D,D,D,D,D,D,D
two,you,can,tell,if,its,picking,up
2,2,2,2,2,2,2,2
```
In the above example:
Row 1 gives the sequence of tokens in reference transcript. 
Row 2 is the speaker label for each tokens in reference sequence.
Row 3 should be the sequence of tokens in hypothesis transcripts.
Row 4 has the speaker label for each tokens in hypothesis sequence.

### 2. Run the align.py script
Once your transcripts are prepared, run the provided align.py script. This script aligns the hypothesis and reference
transcripts to generate a JSON file.
Here's how you can do it:
```
python align.py inputfile.csv -o outputfile.json
```
The `inputfile.csv` should be following the format as step 1 mentioned. The `outputfile.json` is optional. If no output
name specified, the output will be written in `inputfile.json`.

### 3. Run TranscribeView
After creating the alignment JSON file, we can finally use transcribeView to evaluate it.
The following command opens up a browser window for the TranscribeView System.
```shell
streamlit run transcribeView.py

```

Finally, upload the JSON file in the upper left section.