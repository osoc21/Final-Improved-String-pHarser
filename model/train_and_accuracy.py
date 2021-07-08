import argparse
import sys
import subprocess
import os
import csv

'''
Example usage: python3 train_and_accuracy.py examples.csv train_ratio (between [0, 1])
'''

# Parse the command line arguments
# examples is the full examples file
# train_ratio is the ratio of train examples that should be taken from the full example dataset
parser = argparse.ArgumentParser(description='Train CSV file with Anystyle and get accuracy.')
parser.add_argument('examples', metavar='N', type=str, nargs='+',
                    help='All examples as a CSV file.')
parser.add_argument('train_ratio', metavar='N', type=float, nargs='+',
                    help='Proportion of examples to take as training.')

all_examples_file_name = sys.argv[1]
train_examples_ratio = float(sys.argv[2])

# Open the examples file
all_examples_file = open(all_examples_file_name, "r", encoding="utf-8")

# Count the total amount of examples
amount_of_examples = sum(1 for line in open(all_examples_file_name, encoding="utf-8"))
# Calculate the amount of train examples
train_examples_amount = int(train_examples_ratio * amount_of_examples)

# Open a train examples CSV file to store the train examples
train_file_name = 'train_examples.csv'
train_file = open('train_examples.csv', 'w', encoding="utf-8")
train_writer = csv.writer(train_file)

# Open a test examples CSV file to store the test examples
test_file_name = 'test_examples.csv'
test_file = open('test_examples.csv', 'w', encoding="utf-8")
test_writer = csv.writer(test_file)

# Read out all lines of the full examples and split into train and test examples.
csv_reader = csv.DictReader(all_examples_file)
line_nb = 0
for row in csv_reader:
    line_nb += 1
    # The first line is the header and should be in both files
    if line_nb == 1:
        header = row.keys()
        train_writer.writerow(header)
        test_writer.writerow(header)
    else:
        # Add line to train examples if it is in n first lines
        if line_nb < train_examples_amount:
            train_writer.writerow(row.values())
        # else add to test examples
        else:
            test_writer.writerow(row.values())

# close the files
train_file.close()
test_file.close()

# Convert train examples CSV file to XML file
xml_train_file_name = "train-examples.xml"
subprocess.check_output('python3 csv2xml.py ' + train_file_name + ' ' + xml_train_file_name, shell=True)

# Convert test examples CSV file to XML file
xml_test_file_name = "test_examples.xml"
subprocess.check_output('python3 csv2xml.py ' + test_file_name + ' ' + xml_test_file_name, shell=True)

model_file_name = "out.mod"
# Delete output model file if it already exists
if os.path.exists(model_file_name):
    os.remove(model_file_name)

# Train the model
subprocess.check_output('anystyle train ' + xml_train_file_name + ' ' + model_file_name, shell=True)

# Test the model
data = subprocess.check_output('anystyle -P ' + model_file_name + ' check ' + xml_test_file_name, shell=True)

# Decode the byte string to a string
data = data.decode("utf-8")

# Print results
print(data)
print(data.split(" ")[7] + " error rate")
