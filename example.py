import os
from grobid_client.grobid_client import GrobidClient
import shutil
import xmltodict
import json
import argparse

parser = argparse.ArgumentParser(description='Process PDF file.')
parser.add_argument('file_path', type=str, help='PDF file path')
parser.add_argument('file_name', type=str, help='PDF file name')

args = parser.parse_args()
file_name = args.file_name
file_path = args.file_path

f = open("out.txt", "w")

# put input pdf in a directory called filedir
# make a directory

if not os.path.exists(file_path):
    os.makedirs(file_path)
# put input file in the directory
GROBID_PATH = "grobid_client_python/"
os.chdir(GROBID_PATH)

#os.chdir("grobid_client_python/temp/")
file_path = "grobid_client_python/temp"
shutil.copyfile(file_name, file_path + "/input.pdf")
f.write("done moving file\n")
# read all the pdf's inside the directory created and put the parsed string there
client = GrobidClient(config_path="grobid_client_python/config.json")
# calls their service
client.process("processReferences", file_path, output=file_path,
               consolidate_citations=True, teiCoordinates=True, force=True)

# retrive file with parsed citation (and convert html to JSON)
with open(file_path + "/input.tei.xml", 'r', encoding="utf8") as file:
    obj = file.read()
    #json_data = json.dumps(xmltodict.parse(obj))
# clear directory
print(obj)

for filename in os.listdir(file_path):
    out_path = os.path.join(file_path, filename)
    try:
        if os.path.isfile(out_path) or os.path.islink(out_path):
            os.unlink(out_path)
        elif os.path.isdir(out_path):
            shutil.rmtree(out_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (out_path, e))
f.write(obj)
# print(process_file('/home/felix/test1.pdf'))


# if __name__ == "__main__":
# client = GrobidClient(config_path="./config.json")
# client.process("processReferences", "C:/Users/wensm/grobid_client_python", output="C:/stage/Grobid/output", consolidate_citations=True, teiCoordinates=True, force=True)
# os.system('curl -X POST -d "citations=Graff, Expert. Opin. Ther. Targets (2002) 6(1): 103-113" localhost:8080/api/processCitation')
