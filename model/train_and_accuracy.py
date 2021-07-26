import argparse
import sys
import subprocess
import os
import csv
import json
import re

'''
Example usage: python3 train_and_accuracy.py examples.csv train_ratio [--start 2000] [--end 2021] [--out out.mod]
'''

CSV_DATA_PATH = "data/csv/"
TEMP_DATA_PATH = "data/tmp/"
XML_DATA_PATH = "data/xml/"
MODEL_DATA_PATH = "data/models/"

# Parse the command line arguments
# examples is the full examples file
# train_ratio is the ratio of train examples that should be taken from the full example dataset
parser = argparse.ArgumentParser(description='Train CSV file with Anystyle and get accuracy.')
parser.add_argument('examples', metavar='examples.csv', type=str,
                    help='All examples as a CSV file.')
parser.add_argument('train_ratio', metavar='float', type=float,
                    help='Proportion of examples to take as training.')
parser.add_argument('--start', metavar='int', type=int, default=0,
                    help='Starting year for the citations to train.', required=False)
parser.add_argument('--end', metavar='int', type=int, default=sys.maxsize,
                    help='End year for the citations to train.', required=False)
parser.add_argument('--out', metavar='out.mod', type=str, default="out.mod",
                    help='Output file name fot the learned models', required=False)

args = parser.parse_args()

# Put the command line variables in to python variables
all_examples_file_name = args.examples
train_examples_ratio = args.train_ratio
start_year = args.start
end_year = args.end
model_file_name = args.out

# As file at filePath is deleted now, so we should check if file exists or not not before deleting them
if os.path.exists(MODEL_DATA_PATH + model_file_name):
    os.remove(MODEL_DATA_PATH + model_file_name)

# Open the examples file
all_examples_file = open(CSV_DATA_PATH + all_examples_file_name, "r", newline='\n', encoding="utf-8")

# Open a train examples CSV file to store the train examples
train_file_name = 'train_examples.csv'
train_file = open(TEMP_DATA_PATH + train_file_name, 'w', newline='\n', encoding="utf-8")
train_writer = csv.writer(train_file)

# Open a test examples CSV file to store the test examples
test_file_name = 'test_examples.csv'
test_file = open(TEMP_DATA_PATH + test_file_name, 'w', newline='\n', encoding="utf-8")
test_writer = csv.writer(test_file)

# Read out all lines of the full examples and split into train and test examples.
csv_reader = csv.DictReader(all_examples_file)
line_nb = 0
train_examples_count = 0
test_examples_count = 0

# Count amount of examples are in the year range
amount_of_examples_in_range = 0
for row in csv_reader:
    line_nb += 1
    try:
        year = int(row["Year"])
        if start_year <= year <= end_year:
            amount_of_examples_in_range += 1
    except ValueError:
        pass

train_examples_amount = int(train_examples_ratio * amount_of_examples_in_range)
# Reset the file reader to the beginning of the file
all_examples_file.seek(0)
line_nb = 0

for row in csv_reader:
    line_nb += 1
    # The first line is the header and should be in both files
    if line_nb == 1:
        header = row.keys()
        train_writer.writerow(header)
        test_writer.writerow(header)
    else:
        try:
            year = int(row["Year"])
        except ValueError:
            year = -1
        if start_year <= year <= end_year:
            # Add line to train examples if it is in n first lines
            if train_examples_count < train_examples_amount:
                train_writer.writerow(row.values())
                train_examples_count += 1
            # else add to test examples
            else:
                test_writer.writerow(row.values())
                test_examples_count += 1

# close the files
train_file.close()
test_file.close()

print("Train examples: {}".format(train_examples_count))
print("Test examples: {}".format(test_examples_count))

# Convert train examples CSV file to XML file
xml_train_file_name = "train_examples.xml"
subprocess.check_output('python3 csv2xml.py ' + TEMP_DATA_PATH + train_file_name + ' ' + XML_DATA_PATH + xml_train_file_name, shell=True)

# Convert test examples CSV file to XML file
xml_test_file_name = "test_examples.xml"
subprocess.check_output('python3 csv2xml.py ' + TEMP_DATA_PATH + test_file_name + ' ' + XML_DATA_PATH + xml_test_file_name, shell=True)

# Delete output models file if it already exists
if os.path.exists(model_file_name):
    os.remove(model_file_name)

# Train the models
subprocess.check_output('anystyle train ' + XML_DATA_PATH + xml_train_file_name + ' ' + MODEL_DATA_PATH + model_file_name, shell=True)

# Test the models
data = subprocess.check_output('anystyle -P ' + MODEL_DATA_PATH + model_file_name + ' check ' + XML_DATA_PATH + xml_test_file_name, shell=True)

# Analyse the result for each citation part
output = subprocess.check_output('anystyle -P ' + MODEL_DATA_PATH + model_file_name + ' -f json parse ' + TEMP_DATA_PATH + test_file_name, shell=True)

outputJSON = json.loads(output)

test_file = open(TEMP_DATA_PATH + test_file_name, 'r', newline='\n', encoding="utf-8")

columns = ["Authors", "Year", "Title", "Book", "Series", "Publisher", "City", "Volume", "Issue", "Pagination", "DOI"]
line_nb = 1
mismatches = 0
errors = 0
csv_reader = csv.DictReader(test_file)

# Count the total amount of mismatched citation parts and the total amount of missing citation parts.
# A citation part is mismatched if the model makes a prediction for that citation part but it is incorrect
# A citation part is missing if the prediction has no prediction for that part but it is expected from the test example
totalParts = 0
for line in csv_reader:
    if line_nb >= 1:
        for citationKey in columns:
            totalParts += 1
            try:
                expected = line[citationKey]
                expected = re.sub(r'[^A-Za-z0-9 ]+', '', expected)
                if expected != "":
                    predicted = outputJSON[line_nb][citationKey][0]
                    predicted = re.sub(r'[^A-Za-z0-9 ]+', '', predicted)

                    if expected != predicted:
                        # print("Expected" + citationKey + " : " + str(expected))
                        # print("Predicted" + citationKey + " : " + str(predicted))
                        mismatches += 1
            except KeyError:
                errors += 1
    line_nb += 1

# Decode the byte string to a string
data = data.decode("utf-8")

# Print results
print(data)
res = [i for i in data.split() if "%" in i]
print("Parts errors rate ", (mismatches+errors)/totalParts * 100)
print("Error rate {}".format(res[0]))
print("Token error rate {}".format(res[1]))
