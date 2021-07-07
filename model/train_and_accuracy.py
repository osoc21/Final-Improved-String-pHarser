import argparse
import sys
import subprocess
import os
import csv

'''
Example usage: python3 train_and_accuracy train_examples.csv test_examples.csv
'''
parser = argparse.ArgumentParser(description='Train CSV file with Anystyle and get accuracy.')
parser.add_argument('examples', metavar='N', type=str, nargs='+',
                    help='All examples as a CSV file.')
parser.add_argument('train_ratio', metavar='N', type=float, nargs='+',
                    help='Proportion of examples to take as training.')

all_examples_file_name = sys.argv[1]
train_examples_ratio = float(sys.argv[2])

all_examples_file = open(all_examples_file_name, "r")
amount_of_examples = sum(1 for line in open(all_examples_file_name))
train_examples_amount = int(train_examples_ratio * amount_of_examples)

train_file_name = 'train_examples.csv'
train_file = open('train_examples.csv', 'w')
train_writer = csv.writer(train_file)

test_file_name = 'test_examples.csv'
test_file = open('test_examples.csv', 'w')
test_writer = csv.writer(test_file)

csv_reader = csv.DictReader(all_examples_file)
line_nb = 0
for row in csv_reader:
    line_nb += 1
    if line_nb == 1:
        header = row.keys()
        train_writer.writerow(header)
        test_writer.writerow(header)
    else:
        if line_nb < train_examples_amount:
            # create the csv writer
            # write a row to the csv file
            train_writer.writerow(row.values())
        else:
            test_writer.writerow(row.values())

# close the files
train_file.close()
test_file.close()

xml_train_file_name = "train_examples.xml"
subprocess.check_output('python3 csv2xml.py ' + train_file_name + ' ' + xml_train_file_name, shell=True)

xml_test_file_name = "test_examples.xml"
subprocess.check_output('python3 csv2xml.py ' + test_file_name + ' ' + xml_test_file_name, shell=True)

model_file_name = "out.mod"


if os.path.exists(model_file_name):
    os.remove(model_file_name)

subprocess.check_output('anystyle train ' + xml_train_file_name + ' ' + model_file_name, shell=True)
data = subprocess.check_output('anystyle -P ' + model_file_name + ' check ' + xml_test_file_name, shell=True)

print(data)
#subprocess.check_output("anystyle train " + train_examples + " " + "out.mod")