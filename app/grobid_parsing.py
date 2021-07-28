import os
from grobid_client.grobid_client.grobid_client import GrobidClient
import shutil
import xmltodict
import json
import argparse
import sys
import pathlib

parser = argparse.ArgumentParser(description='Process PDF file.')
parser.add_argument('file_path', type=str, help='PDF file path')
parser.add_argument('file_name', type=str, help='PDF file name')

args = parser.parse_args()
file_name = args.file_name
file_path = args.file_path

# put input pdf in a directory called filedir
# make a directory

if not os.path.exists(file_path):
    os.makedirs(file_path)
# put input file in the directory
GROBID_PATH = "/app/grobid_client/"
os.chdir(GROBID_PATH)

# read all the pdf's inside the directory created and put the parsed string there
client = GrobidClient(config_path="config.json")
# calls their service
client.process("processReferences", GROBID_PATH, output=GROBID_PATH,
               consolidate_citations=True, teiCoordinates=True, force=True)

pdf_file = os.path.basename(file_name).rstrip(".pdf")

def log_to_docker(msg):
    print(msg, file=sys.stderr)

log_to_docker(os.listdir(GROBID_PATH))
log_to_docker(os.getcwd())

log_to_docker(str(next(pathlib.Path("/").rglob("*tei.xml"))))
# retrive file with parsed citation (and convert html to JSON)
with open(GROBID_PATH + f"{pdf_file}.tei.xml", 'r', encoding="utf8") as file:
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
