import subprocess
import json
import re
import csv
import statistics
from os import listdir
from os.path import isfile, join

# Script that compares performance of a citation when using the full model vs when using a model based on the year.

MODEL_FILE_NAME = "examples-2251.mod"
TEST_CSV_FILE_NAME = "examples-aphia.csv"
OUTPUT_XML_FILE_NAME = "examples-aphia.xml"

YEARS_MODELS_PATH = "data/models/year_models/"
CSV_PATH = "data/csv/"
BASE_MODELS_PATH = "data/models/"
XML_PATH = "data/xml/"

base_model_file_name = BASE_MODELS_PATH + MODEL_FILE_NAME
test_csv_file_name = CSV_PATH + TEST_CSV_FILE_NAME
output = subprocess.check_output('anystyle -P ' + base_model_file_name +
                                 ' -f json parse ' + test_csv_file_name, shell=True)

outputJsonBase = json.loads(output)


file_names = [f for f in listdir(YEARS_MODELS_PATH) if isfile(join(YEARS_MODELS_PATH, f))]

test_xml_file_name = XML_PATH + OUTPUT_XML_FILE_NAME

subprocess.check_output('python3 csv2xml.py ' + test_csv_file_name + ' ' + test_xml_file_name, shell=True)

columns = ["Authors", "Year", "Title", "Book", "Series", "Publisher", "City", "Volume", "Issue", "Pagination", "DOI"]
test_csv_file = open(test_csv_file_name, "r")
csv_reader = csv.DictReader(test_csv_file)
line_nb = 0

missingRatioYears = []
missingRatioBase = []

mismatchedRatioYears = []
mismatchedRatioBase = []
total_examples = sum(1 for row in csv_reader)
nb = 1
test_csv_file.seek(0)

mistakesMapFullModel = {}
for citationKey in columns:
    mistakesMapFullModel[citationKey] = 0

errorsMapFullModel = {}
for citationKey in columns:
    errorsMapFullModel[citationKey] = 0

mistakesMapYearModel = {}
for citationKey in columns:
    mistakesMapYearModel[citationKey] = 0

errorsMapYearModel = {}
for citationKey in columns:
    errorsMapYearModel[citationKey] = 0

partsCount = {}
for citationKey in columns:
    partsCount[citationKey] = 0

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

        errorsYear = 0
        errorsBase = 0

        for file_name in file_names:
            year_range = file_name.split(".")[0].split("-")

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
                        else:
                            errorsYear += 1
                            errorsMapYearModel[citationKey] += 1

                    if citationKey in line:
                        expected = line[citationKey]
                        expected = re.sub(r'[^A-Za-z0-9 ]+', '', expected)
                        if expected != "" and citationKey in outputJsonBase[line_nb]:
                            predictedBase = outputJsonBase[line_nb][citationKey][0]
                            predictedBase = re.sub(r'[^A-Za-z0-9 ]+', '', predictedBase)
                            if expected != predictedBase:
                                mismatchesBase += 1
                                mistakesMapFullModel[citationKey] += 1
                        else:
                            errorsBase += 1
                            errorsMapFullModel[citationKey] += 1
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

        print("========= Progress ==========")
        print(str(line_nb/total_examples * 100) + "%")
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
        ratioErrorsYearMap = {}
        for key, value in errorsMapYearModel.items():
            if partsCount[key] > 0:
                ratioErrorsYearMap[key] = errorsMapYearModel[key] / partsCount[key]
        ratioMistakesFullMap = {}
        for key, value in mistakesMapFullModel.items():
            if partsCount[key] > 0:
                ratioMistakesFullMap[key] = mistakesMapFullModel[key] / partsCount[key]
        ratioErrorsFullMap = {}
        for key, value in errorsMapFullModel.items():
            if partsCount[key] > 0:
                ratioErrorsFullMap[key] = errorsMapFullModel[key] / partsCount[key]
        print("========= Year model ==========")
        print(f"Amount of mistakes {ratioMistakesYearMap}")
        print(f"Errors {ratioErrorsYearMap}")

        print("========= Full model ==========")
        print(f"Amount of mistakes {ratioMistakesFullMap}")
        print(f"Errors {ratioErrorsFullMap}")
