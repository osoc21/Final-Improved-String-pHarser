import subprocess
import json
import re
import csv
import statistics
from os import listdir
from os.path import isfile, join

# Script that compares performance of a citation when using the full/base model vs when using a model based on the year.
# For the years model the full model is first used to find the year of a citation. With this year the correct year model
# is selected. So for instance a citation of 2008 will be parsed with 2001-2011.mod

# Name of model file to compare to years model
MODEL_FILE_NAME = "examples-2251.mod"
# Name of csv file of examples to test on. These must be labeled
TEST_CSV_FILE_NAME = "examples-aphia.csv"
# Name of xml file that csv file will be converted to for anystyle readability
OUTPUT_XML_FILE_NAME = "examples-aphia.xml"

# Location of year models
YEARS_MODELS_PATH = "data/models/year_models/"
# Location of test file
CSV_PATH = "data/csv/"
# Location of model file
BASE_MODELS_PATH = "data/models/"
# Location for output xml file
XML_PATH = "data/xml/"

base_model_file_name = BASE_MODELS_PATH + MODEL_FILE_NAME
test_csv_file_name = CSV_PATH + TEST_CSV_FILE_NAME

# Let anystyle parse the csv test file and return the json with predicted values
output = subprocess.check_output('anystyle -P ' + base_model_file_name +
                                 ' -f json parse ' + test_csv_file_name, shell=True)

# Parse the returned JSON from anystyle
outputJsonBase = json.loads(output)

# Search all year models
file_names = [f for f in listdir(YEARS_MODELS_PATH) if isfile(join(YEARS_MODELS_PATH, f))]

test_xml_file_name = XML_PATH + OUTPUT_XML_FILE_NAME

#subprocess.check_output('python3 csv2xml.py ' + test_csv_file_name + ' ' + test_xml_file_name, shell=True)

# All possible fields for citation parts
columns = ["Authors", "Year", "Title", "Book", "Series", "Publisher", "City", "Volume", "Issue", "Pagination", "DOI"]
test_csv_file = open(test_csv_file_name, "r")
csv_reader = csv.DictReader(test_csv_file)
line_nb = 0

# Missing ratios for both the years and base model
# A citation part is missing if no prediction is made by the model but is expected from the test examples
missingRatioYears = []
missingRatioBase = []

# Mismatched ratios for both the years and base model
# A citation part is mismatched if a prediction is made by the model but is different to the expected part from
# the test examples
mismatchedRatioYears = []
mismatchedRatioBase = []


total_examples = sum(1 for row in csv_reader)
nb = 1
test_csv_file.seek(0)

# Initialize all dictionaries for the counting
mistakesMapFullModel = {}
for citationKey in columns:
    mistakesMapFullModel[citationKey] = 0

missingMapFullModel = {}
for citationKey in columns:
    missingMapFullModel[citationKey] = 0

mistakesMapYearModel = {}
for citationKey in columns:
    mistakesMapYearModel[citationKey] = 0

missingMapYearModel = {}
for citationKey in columns:
    missingMapYearModel[citationKey] = 0

partsCount = {}
for citationKey in columns:
    partsCount[citationKey] = 0

# For each example count the mismatched and the missing parts for each model
for line in csv_reader:

    line_nb += 1

    if line_nb < len(outputJsonBase):
        year = 0
        if "Year" in outputJsonBase[line_nb] and outputJsonBase[line_nb]["Year"] is not None:
            year = outputJsonBase[line_nb]["Year"][0]
            year = re.sub(r'[^A-Za-z0-9 ]+', '', year)
        totalParts = 0
        mismatchesYear = 0
        mismatchesBase = 0

        missingYear = 0
        missingBase = 0
        # If there is a year found, the year models can be used. If no year found with the full model, no year model
        # will be used
        for file_name in file_names:
            year_range = file_name.split(".")[0].split("-")
            # Select the correct year model
            if int(year_range[0]) <= int(year) <= int(year_range[1]):
                output = subprocess.check_output('anystyle -P ' + YEARS_MODELS_PATH + file_name +
                                                 ' -f json parse ' +
                                                 test_xml_file_name,
                                                 shell=True)
                outputJsonYear = json.loads(output)

                for citationKey in columns:
                    if citationKey in line and citationKey != "String" and line[citationKey] != "":
                        totalParts += 1
                        partsCount[citationKey] += 1
                    if citationKey in line:
                        expected = line[citationKey]

                        expected = re.sub(r'[^A-Za-z0-9 ]+', '', expected)

                        if expected != "" and citationKey in outputJsonYear[line_nb - 1]:
                            predicted = outputJsonYear[line_nb-1][citationKey][0]
                            predicted = re.sub(r'[^A-Za-z0-9 ]+', '', predicted)
                            if expected != predicted:
                                # print("Expected" + citationKey + " : " + str(expected))
                                # print("Predicted" + citationKey + " : " + str(predicted))
                                mismatchesYear += 1
                                mistakesMapYearModel[citationKey] += 1
                        elif expected != "":
                            missingYear += 1
                            missingMapYearModel[citationKey] += 1

                    if citationKey in line:
                        expected = line[citationKey]
                        expected = re.sub(r'[^A-Za-z0-9 ]+', '', expected)
                        if expected != "" and citationKey in outputJsonBase[line_nb]:
                            predictedBase = outputJsonBase[line_nb][citationKey][0]
                            predictedBase = re.sub(r'[^A-Za-z0-9 ]+', '', predictedBase)
                            if expected != predictedBase:
                                mismatchesBase += 1
                                mistakesMapFullModel[citationKey] += 1
                        elif expected != "":
                            missingBase += 1
                            missingMapFullModel[citationKey] += 1
                outputJsonYear = json.loads(output)
        # Print out the statistics for this example
        print("========= Year model ==========")
        print(f"Total citation parts {totalParts}")
        print(f"Total mismatched parts {mismatchesYear}")
        print(f"Total missing parts {missingYear}")
        if totalParts > 0:
            mismatchedRatioYears.append(mismatchesYear/totalParts)
            missingRatioYears.append(missingYear/totalParts)

        print("========= Full model ==========")
        print(f"Total citation parts {totalParts}")
        print(f"Total mismatched parts {mismatchesBase}")
        print(f"Total missing parts {missingBase}")
        if totalParts > 0:
            mismatchedRatioBase.append(mismatchesBase/totalParts)
            missingRatioBase.append(missingBase/totalParts)

        # Print out the progress made
        print("========= Progress ==========")
        print(str(line_nb/total_examples * 100) + "%")

        # Print out the statistics for all examples parsed up to now
        if len(missingRatioYears) > 1:
            print("========= Statistics ==========")

            print(f"Mismatched ratio years model {statistics.mean(mismatchedRatioYears)}")
            print(f"Missing ratio years model {statistics.mean(missingRatioYears)}")

            print(f"Mismatched ratio base model {statistics.mean(mismatchedRatioBase)}")
            print(f"Missing ratio base model {statistics.mean(missingRatioBase)}")

        print("========= Detailed statistics ==========")
        ratioMistakesYearMap = {}
        for key, value in mistakesMapYearModel.items():
            if partsCount[key] > 0:
                ratioMistakesYearMap[key] = mistakesMapYearModel[key] / partsCount[key]
        ratioMissingYearMap = {}
        for key, value in missingMapYearModel.items():
            if partsCount[key] > 0:
                ratioMissingYearMap[key] = missingMapYearModel[key] / partsCount[key]
        ratioMistakesFullMap = {}
        for key, value in mistakesMapFullModel.items():
            if partsCount[key] > 0:
                ratioMistakesFullMap[key] = mistakesMapFullModel[key] / partsCount[key]
        ratioMissingFullMap = {}
        for key, value in missingMapFullModel.items():
            if partsCount[key] > 0:
                ratioMissingFullMap[key] = missingMapFullModel[key] / partsCount[key]
        
        # Print out more detailed statistics, showing for each citation field the missing and mistakes ratio
        print("========= Year model ==========")
        print(f"Amount of mistakes {ratioMistakesYearMap}")
        print(f"Missing {ratioMissingYearMap}")

        print("========= Full model ==========")
        print(f"Amount of mistakes {ratioMistakesFullMap}")
        print(f"Missing {ratioMissingFullMap}")
