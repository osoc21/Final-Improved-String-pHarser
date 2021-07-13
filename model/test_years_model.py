import subprocess
import json
import re
import csv
import statistics
from os import listdir
from os.path import isfile, join

# Script that compares performance of a citation when using the full model vs when using a model based on the year.

YEARS_MODELS_PATH = "data/models/year_models/"
CSV_PATH = "data/csv/"
BASE_MODELS_PATH = "data/models/"
XML_PATH = "data/xml/"

base_model_file_name = BASE_MODELS_PATH + "examples-2000.mod"
test_csv_file_name = CSV_PATH + "examples-2251.csv"
output = subprocess.check_output('anystyle -P ' + base_model_file_name +
                                 ' -f json parse ' + test_csv_file_name, shell=True)

outputJsonBase = json.loads(output)


file_names = [f for f in listdir(YEARS_MODELS_PATH) if isfile(join(YEARS_MODELS_PATH, f))]

test_xml_file_name = XML_PATH + "examples-2251.xml"

subprocess.check_output('python3 csv2xml.py ' + test_csv_file_name + ' ' + test_xml_file_name, shell=True)

columns = ["Authors", "Year", "Title", "Book", "Series", "Publisher", "City", "Volume", "Issue", "Pagination", "DOI"]
test_csv_file = open(test_csv_file_name, "r")
csv_reader = csv.DictReader(test_csv_file)
line_nb = 0

missingRatioYears = []
missingRatioBase = []

mismatchedRatioYears = []
mismatchedRatioBase = []

nb = 1
for line in csv_reader:
    try:
        line_nb += 1
        year = outputJsonBase[line_nb]["Year"][0]
        year = re.sub(r'[^A-Za-z0-9 ]+', '', year)

        totalParts = 0
        mismatchesYear = 0
        mismatchesBase = 0

        errorsYear = 0
        errorsBase = 0

        for file_name in file_names:
            year_range = file_name.split(".")[0].split("-")
            if year_range[0] <= year <= year_range[1]:
                output = subprocess.check_output('anystyle -P ' + YEARS_MODELS_PATH + file_name +
                                                 ' -f json parse ' +
                                                 test_xml_file_name,
                                                 shell=True)
                outputJsonYear = json.loads(output)

                for citationKey in columns:
                    if line_nb > 1 and line[citationKey] != "":
                        totalParts += 1
                    try:
                        expected = line[citationKey]
                        expected = re.sub(r'[^A-Za-z0-9 ]+', '', expected)
                        if expected != "":
                            predicted = outputJsonYear[line_nb-1][citationKey][0]
                            predicted = re.sub(r'[^A-Za-z0-9 ]+', '', predicted)
                            if expected != predicted:
                                # print("Expected" + citationKey + " : " + str(expected))
                                # print("Predicted" + citationKey + " : " + str(predicted))
                                mismatchesYear += 1
                    except KeyError:
                        errorsYear += 1
                    try:
                        expected = line[citationKey]
                        expected = re.sub(r'[^A-Za-z0-9 ]+', '', expected)
                        if expected != "":
                            predictedBase = outputJsonBase[line_nb][citationKey][0]
                            predictedBase = re.sub(r'[^A-Za-z0-9 ]+', '', predictedBase)
                            if expected != predictedBase:
                                mismatchesBase += 1
                    except KeyError:
                        errorsBase += 1
                outputJsonYear = json.loads(output)

        print("========= Year model ==========")
        print(f"Total citation parts {totalParts}")
        print(f"Total mismatched parts {mismatchesYear}")
        print(f"Total missing parts {errorsYear}")
        if totalParts > 0:
            mismatchedRatioYears.append(mismatchesYear/totalParts)
            missingRatioYears.append(errorsYear/totalParts)

        print("========= Full model ==========")
        print(f"Total citation parts {totalParts}")
        print(f"Total mismatched parts {mismatchesBase}")
        print(f"Total missing parts {errorsBase}")
        if totalParts > 0:
            mismatchedRatioBase.append(mismatchesBase/totalParts)
            missingRatioBase.append(errorsBase/totalParts)

    except KeyError:
        print("No year found in full model.")


print("========= ----------- ==========")

print(f"Mismatched ratio years model {statistics.mean(mismatchedRatioYears)}")
print(f"Missing ratio years model {statistics.mean(missingRatioYears)}")

print(f"Mismatched ratio base model {statistics.mean(mismatchedRatioBase)}")
print(f"Missing ratio base model {statistics.mean(missingRatioBase)}")

