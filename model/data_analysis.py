import csv
import argparse
from matplotlib import pyplot as plt
import numpy as np

# Usage: python3 data_analysis.py examples.csv
parser = argparse.ArgumentParser(description='Train CSV file with Anystyle and get accuracy.')
parser.add_argument('examples', metavar='examples.csv', type=str,
                    help='All examples as a CSV file.')

args = parser.parse_args()

# Put the command line variables in to python variables
all_examples_file_name = args.examples

# Open the examples file
all_examples_file = open(all_examples_file_name, "r", newline='\n', encoding="utf-8")
csv_reader = csv.DictReader(all_examples_file)
line_nb = 0
train_examples_count = 0
test_examples_count = 0

# Count amount of examples are in the year range
amount_of_examples_in_range = 0
all_years = []
for row in csv_reader:
    line_nb += 1
    try:
        year = int(row["Year"])
        if year != 300000:
            all_years.append(year)
    except ValueError:
        pass

all_years.sort()
print(all_years)

data = np.array(all_years)

n, bins, patches = plt.hist(x=data, bins='auto', color='#0504aa',
                            alpha=0.7, rwidth=0.85)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Year')
plt.ylabel('Amount of citations')
plt.title('Years of citations')
plt.text(23, 45, r'$\mu=15, b=3$')
maxfreq = n.max()
# Set a clean upper y-axis limit.
plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)
plt.show()