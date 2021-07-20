import os
from grobid_client.grobid_client import GrobidClient
import shutil
import xmltodict
import json

if __name__ == "__main__":
    def process_file(InputPDF):
        # put input pdf in a directory called filedir
        # make a directory
        filedir = "C:/Users/wensm/grobid_client_python/TempPDF"
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        # put input file in the directory
        shutil.copyfile(InputPDF, filedir + "/input.pdf")

        # read all the pdf's inside the directory created and put the parsed string there
        client = GrobidClient(config_path="./config.json")
        client.process("processReferences", filedir, output= filedir,
                        consolidate_citations=True, teiCoordinates=True, force=True)

        # retrive file with parsed citation (and convert html to JSON)
        with open(filedir + "/input.tei.xml", 'r', encoding="utf8") as myfile:
            obj = myfile.read()
            json_data = json.dumps(xmltodict.parse(obj))
        # clear directory
        for filename in os.listdir(filedir):
            file_path = os.path.join(filedir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        # return retrieved file
        return json_data


    print(process_file('C:/Users/wensm/grobid_client_python/test1.pdf'))


# if __name__ == "__main__":
# client = GrobidClient(config_path="./config.json")
# client.process("processReferences", "C:/Users/wensm/grobid_client_python", output="C:/stage/Grobid/output", consolidate_citations=True, teiCoordinates=True, force=True)
# os.system('curl -X POST -d "citations=Graff, Expert. Opin. Ther. Targets (2002) 6(1): 103-113" localhost:8080/api/processCitation')

