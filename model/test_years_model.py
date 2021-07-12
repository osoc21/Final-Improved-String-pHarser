import subprocess
import json
import re
from os import listdir
from os.path import isfile, join
# TODO: use csv2xml
PATH = "data/models/year_models/"
model_file_name = "out.mod"
test_file_name = "data/csv/one_example.csv"
output = subprocess.check_output('anystyle -P ' + model_file_name + ' -f json parse ' + test_file_name, shell=True)

outputJSON = json.loads(output)

year = outputJSON[0]["Year"][0]
print(outputJSON)
year = re.sub(r'[^A-Za-z0-9 ]+', '', year)

file_names = [f for f in listdir(PATH) if isfile(join(PATH, f))]

for file_name in file_names:
    year_range = file_name.split(".")[0].split("-")
    if year_range[0] <= year <= year_range[1]:
        output = subprocess.check_output('anystyle -P ' + PATH + file_name + ' -f json parse ' + test_file_name,
                                             shell=True)
        outputJSON = json.loads(output)
        print(outputJSON)

