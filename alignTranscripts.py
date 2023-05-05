# import align4d
import argparse
import csv


parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Input file path')

# # Add an optional argument for the output file
# parser.add_argument('-o', '--output-file', help='Output file path')

def read_input(path):
  with open(path) as f:
    reader = csv.reader(f)
    rows = []
    for row in reader:
      rows.append(row)
  return row[0], row[1], row[2], row[3]

if __name__ == "__main__":
  # Parse the command line arguments
  args = parser.parse_args()

  # Access the values of the arguments
  input_file = args.input_file
  
  # Use the values of the arguments in your code
  print(f'Input file path: {input_file}')
