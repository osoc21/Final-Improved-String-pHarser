# tester

# POST fish.com/ DATA --> return json

from flask import Flask, render_template, request, redirect
from flask_swagger_ui import get_swaggerui_blueprint
import subprocess
import os
import shutil
import time
import csv
import json
import pathlib
import threading
import xml.etree.cElementTree as ET

from flask.helpers import send_from_directory

api = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/Fish-0.1-swagger.yaml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Final-Improved-String-pHarser"
    }
)
api.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

temporary_folder = "temp/"
model_folder = "model/data/models/available_models"
GROBID_PATH = "grobid_client/"
CITATION_STRING_CONST = "citationstring"


@api.route('/', methods=['GET', 'POST'])
def get_homepage():
    models = list(model_folder_path.rglob("*.mod"))

    if request.method == "GET":
        return render_template("index.html", models=get_all_models())

    # If a post gets done to /, assume the user wants to parse, so call /parse_str()
    elif request.method == "POST":
        return parse_str()

"""
get_all_models: get every .mod file in model_folder_path, and remove the dirname

Example:
  Usage: models = get_all_models()
  Return: [str("aphia.mod"), str("all_examples.mod"))]
"""
def get_all_models():
  file_paths = list(model_folder_path.rglob("*.mod"))
  file_names = []
  for path in file_paths:
    file_names.append(os.path.basename(path))
  return file_names

"""
log: save string into log.txt, which can be read using /getlog. Mainly used for debugging.

Arguments:
  > txt: string to be written to file

Example:
  Usage: log("Debug info: " + debug)
  Return: None
"""
def log(txt):
  with open("log.txt", "a+") as logfile:
    logfile.write(str(txt))
    logfile.write("\n")

"""
/getlog: show the contents of log.txt in a <textarea>
"""
@api.route('/getlog', methods=['GET'])
def get_log():
  # TODO disable or secure this if any sensitive info is logged
  with open("log.txt", "r") as logfile:
    txt = logfile.readlines()

  textarea = f"Logfile content, from new (top) to old (bottom): <textarea style='width: 90vw; height: 90vh;'>"
  txt.reverse()
  for line in txt:
    textarea += line + "\n"
  textarea += "</textarea>"

  return textarea

"""
index_success/index_error: return the HTTP Status Code with the message

Depending on whether the request comes from the website or not, it'll be sent in JSON or in HTML 

Arguments:
  > success_code/error_code: HTTP status code (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
  > success_msg/error_msg: custom text to be added to the response

Example:
  Usage: index_success(200, "OK")  ||  index_error(403, "Forbidden")
  Return: Flask response
"""
def index_success(success_code, success_msg):
  data = {"response": success_msg, "type": "success"}

  if request.values.get('from-website', default=False):
    return render_template('index.html', data=data, models=get_all_models()), success_code, {'Content-Type': 'text/html'}
  else:
    return data, success_code

def index_error(error_code, error_msg):
  data = {"response": error_msg, "type": "error"}
  if request.values.get('from-website', default=False):
    return render_template('index.html', data=data, models=get_all_models()), error_code, {'Content-Type': 'text/html'}
  else:
    return data, error_code


"""
remove_in_background: pass (a) filename(s) to remove (a) file(s), without blocking

Arguments:
  > filenames: a str, or a list(str(),str()) of file paths

Example:
  Usage: remove_in_background(["temp/test.txt", temp_file_path])  ||  remove_in_background("test.xml")
  Return: None
"""
def remove_in_background(filenames):
  if type(filenames) == str:
    filenames = [filenames] 
  threading.Thread(target=remove_files, args=(filenames,)).start()  # , is important

"""
save_data_to_tmp: save the POST data to a random filename in the temp folder, returning the filename afterwards

Arguments:
  > request: the request object
  > ext: the extension to save the file as
  > form_input_name: the name of the form input/header to get data from, if not default

Example:
  Usage: save_data_to_tmp(request, "txt")  ||  save_data_to_tmp(request, "csv", "csv_file")
  Return: str(path_to_randomly_named_file)
"""
# Pass the request object,  the extension and 
def save_data_to_tmp(request, ext,  form_input_name=CITATION_STRING_CONST):
  # To ensure no duplicate filenames, use headers to create a filename
  # This will give issues if two people upload two files with the exact same size on the exact same second
  # This should do the trick for now, but it can be changed later on to a more heavyweight solution if need be
  temp_filename = temporary_folder + request.headers.get("content-length") + time.strftime("%Y%m%d%H%M%S") + "." + ext
  return save_data(request, temp_filename, form_input_name)

"""
save_data: save the POST data to a specified path+filename, returning the filename afterwards

This is used internally by save_data_to_tmp

Arguments:
  > request: the request object
  > filename: path of file to save to
  > form_input_name: the name of the form input/header to get data from, if not default

Example:
  Usage: save_data(request, "model/aphia.xml")  ||  save_data_to_tmp(request, "datastore/test.csv", "csv_file")
  Return: str(path_to_file)
"""
def save_data(request, filename, form_input_name=None):
  # If a string was directly given (no direct file upload), save it to a file
  if len(request.files) <= 0:
    # https://stackoverflow.com/a/42154919  https://stackoverflow.com/a/16966147
    # Either get from form or from request data
    data = request.values.get(form_input_name, request.data.decode("utf-8"))
    log(data)
    file_from_string = open(filename, "w", encoding="utf-8", newline='\n')
    file_from_string.write(data)
    file_from_string.close()
  else:
    # If a file is getting uploaded, save it as well
    request.files['file'].save(filename)
  return filename

"""
/retrain: add (manually corrected) citation data to the training set and retrain the model

This requires the model to have an XML file next to it with its training set
This is done automatically when a model is created using /train, but it might not be the case with externally made models
"""
# Only tested from front-end <form>
@api.route('/retrain', methods=['POST'])
def retrain():
  model_name = request.values.get("model-name") or request.headers.get("model-name")

  log("Retraining " + model_name)

  model_path = select_model(model_name)
  model_data_path = model_path + ".xml"
  model_data = ET.parse(model_data_path)

  dataset = model_data.getroot()
  sequence = ET.SubElement(dataset, "sequence")

  keys = request.values.keys()
  for key in keys:
    log(key)
    # Don't add model-name to XML
    if key == "model-name":
      continue

    value = request.values.get(key)
    log("  " + value)

    
    ET.SubElement(sequence, key).text = value

    
  
  model_data.write(model_data_path)

  return train_model(model_path, model_data_path, overwrite=True)

"""
process_pdf_file: processes a PDF file. The PDF file is processed by calling the GROBID client

This is used internally by parse_pdf

Arguments:
  > file_path: the path of the pdf (str). Including the full name of the PDF file

Example:
  Usage: process_pdf_file(file_path)
  Return: JSON(data_returned_by_grobid)
"""
def process_pdf_file(file_path):
  path = os.path.dirname(file_path)
  path = ''.join(path) + "/"
  file_name = file_path.split("/")[len(file_path.split("/")) - 1]
  #subprocess.check_output('python3 ./hello.py', shell=True)
  log('python3 grobid_client/grobid_parsing.py' + ' ' + path + ' ' +
                                 file_name)
  data = subprocess.check_output('python3 grobid_parsing.py' + ' ' + path + ' ' +
                                 file_name, shell=True)
  return data

"""
parse_pdf: parse a PDF file. The citations in a PDF file are found using process_pdf_file. The response
contains the parsed citations and the original found citations.

This is used internally by /parse-file

Arguments: -

Example:
  Usage: parse_pdf()
  Return: {data=JSON(process_pdf_file(input_filepath)), original_strings=original found citations}
"""
def parse_pdf():
  #model_name = request.headers.get("model-name")
  input_filename = request.files['file'].filename
  input_filepath = GROBID_PATH + input_filename
  # a log statement
  file = request.files['file']
  file.save(input_filename)
  data = process_pdf_file(input_filepath)#, model_name)
  log("data: " + str(data))
  return_data = {
    "data": data,
    "original_strings": ""
  }
  return render_template("response.html", data=return_data)


def get_model_from_request(request):
  try:
    model_name = request.values.get("model-name") or request.headers.get("model-name")
  except KeyError:
    # If model_name not defined, set to empty to grab a random
    model_name = ""
  finally:
    model_name = select_model(model_name)
    return model_name


"""
  Parse citation strings from a html-uploaded file into an array of JSON objects.
  This will automatically decide which filetype it is (csv, plain...)

  URL: domain.com/parse
  Method: POST
  Content-Type: multipart/form-data

  For the form:
    <form enctype="multipart/form-data">
      <input type="file" name="file">
      ...
"""
# parse/file is meant for use in forms. Thus it will simply redirect into the appropiate parse function
@api.route('/parse-file', methods=['POST'])
@api.route('/parse/file', methods=['POST'])
def parse_file():
  if len(request.files) >= 1:
    old_filename = request.files['file'].filename.lower()
    # Check for allowed formats
    if old_filename.endswith("csv"):
      return parse_csv() # redirect("/parse/csv", code=307)  # 307 https://stackoverflow.com/a/15480983
    elif old_filename.endswith("txt") or old_filename.endswith("ref"):
      return parse_str()
    elif old_filename.endswith("pdf"):
      return parse_pdf()
    else:
      # If a non-supported format gets uploaded, return 422
      return index_error(422, "The uploaded file format (" + old_filename[old_filename.rfind("."):] + ") isn't supported.")
  else:
      return index_error(422, "No data found in input")


"""
  parse_csv will convert a csv file into a citation string txt file
  Parse citation strings from a csv string into an array of JSON objects.

  URL: domain.com/parse/csv
  Method: POST
  Headers:
    Ignore_Firstline: {boolean, optional, defaults to True}
      (
        Ignore the firstline. Set to true if first line is a header, for example,: String,Authors,Year...
        Valid values: false, False, true, True, 1, 0
      )
    Single_Column: {int, optional, defaults to -1}
      (
        Only keep the data in the column with index int
        Won't have effect if not set
        Example situation: a csv file with Citationstring,Authors,Year,Title,Book --> use index 0
      )
"""
@api.route('/parse-csv', methods=['POST'])
@api.route('/parse/csv', methods=['POST'])
def parse_csv():
  input_filename = save_data_to_tmp(request, "csv")
  input_filename_csv = input_filename
  input_filename = input_filename_csv.replace("csv", "txt")

  log(request.headers.get("model-name"))
  log(request.headers.get("Single-Column"))

  ignore_firstline = header_boolean(request.headers.get("Ignore-Firstline"), default=True)
  single_column = header_int(request.headers.get("Single-Column"), default=-1)

  log(ignore_firstline)
  log(single_column)

  with open(input_filename_csv, "r", encoding="utf-8", newline='') as original_csv:
    csv_reader = csv.reader(original_csv, delimiter=",")
    csv_data = []
    for row in csv_reader:
      if ignore_firstline:
        ignore_firstline = False  # Don't ignore after the first continue
        continue  # Skip the csv_data append for the first line

      if single_column <= -1:
        csv_data.append(", ".join(row) + "\n")
      else:
        try:
          csv_data.append(row[single_column] + "\n")
        except IndexError:
          pass
    with open(input_filename, "w", encoding="utf-8", newline='\n') as input_file:
      input_file.writelines(csv_data)

  model = get_model_from_request(request)
  return parse_to_citations(input_filename, model, {input_filename, input_filename_csv})
  

"""
  Parse citation strings from plain text, with one citation per line. This is the most ideal method

  URL: domain.com/parse
  Method: POST
"""
@api.route('/parse', methods=['POST'])
@api.route('/parse-string', methods=['POST'])
@api.route('/parse/string', methods=['POST'])
def parse_str():
  input_filename = save_data_to_tmp(request, "txt")
  log("request: " + str(request))
  model = get_model_from_request(request)
  return parse_to_citations(input_filename, model)

def parse_to_citations(filename, model, input_filenames=set()):
  """
  parse_to_citations parses a file containing citations, one citation per line.
  The input file should be converted into a ref or txt file before calling this function, see below
  Pass a str(filename) and str(modelname). Modelname will be automatically recursively searched for, so you don't need to be super precise

  From the documentation we can conclude that a .txt (or a .ref file) with one citation per line is suitable for input:
    https://github.com/inukshuk/anystyle-cli
      The input argument can be a single text document containing one full
      reference per line (blank lines will be ignored), or a folder containing
      multiple documents. The (optional) output argument specifies
      the folder where the results shall be saved; if no output folder is
      specified, results will be saved in the folder containing the input.

      ...

      ref     One reference per line, suitable for parser input;
      txt     Same as `ref';

      ...

      
  Example of a line as provided in a .csv file by VLIZ:
  Krohling, W., & Zalmon, I. R. 2008. Epibenthic colonization on an artificial reef in a stressed environment off the north coast of the Rio de Janeiro State, Brazil. Brazilian Archives of Biology and Technology 51: 213-221.
  """

  input_filenames.add(filename)  # Set of filenames to clean later

  # Step 3: run anystyle and return the result
  data, used_model = process_file(filename, model)

  original_strings = []
  with open(filename, "r", encoding="utf-8", newline='\n') as f:
    lines = f.readlines()
    for line in lines:
      original_strings.append(line.strip("\n"))
    f.close()

  remove_in_background(input_filenames)

  """
  if request.form and CITATION_STRING_CONST not in request.form:
    # TODO: retrain model here
    return index_success(200, "Successfully updated model. Thank you for your contribution")
  """

  return_data = {
    "model": used_model,
    "data": data,
    "original_strings": original_strings
  }

    # If the request comes from the website
  if request.values.get('from-website', default=False):
    return render_template("response.html", data=return_data, model=used_model)
  else:
    return return_data
  

def remove_files(files):
  try:
    for file in files:
      os.remove(file)
    log("Removed")
  except Exception as e:
    log("Error while removing")
    log(e)


def header_boolean(header_value, default):
  # If the header input is a string, make it case insensitive
  if (type(header_value) == str):
    header_value = header_value.lower()
  
  # Check if value in False values (cause bool("False") == True)
  if header_value in ["false", None, False, 0, "0"]:
    value = False

  # Check if value in True values
  elif header_value in ["true", 1]:
    value = True
  
  # Otherwise, use the default value
  else:
    value = default
   
  return value

# Parse an integer value
def header_int(header_value, default=-1):
  try:
    header_value = int(header_value)
  except ValueError:
    return default
  except TypeError:
    return default

  return header_value


"""
process_file: pass a filename, throw it through anystyle, return the response 

It seems like anystyle-cli wants a file to read, and can't handle a direct string input,
but keeping the following line commented in case we find a way to direct it

Arguments:
  > filepath: the path to the file that has to be parsed by anystyle
  > model_name: the name or path of the model you wish to use. If ommited, will default to the latest model.

Example:
  Usage: process_file("citation.txt", "examples-300")
  Return: [str(anystyle json array), str(path to model used)]
"""

model_folder_path = pathlib.Path(model_folder)

def process_file(filepath, model_name=False):

  f = open(filepath, "r", encoding="utf-8", newline='\n')
  altered_lines = []
  for line in f.readlines():
    altered_line = line.replace("\"", "").replace("\r", "")
    altered_lines.append(altered_line)
  f.close()
  f = open(filepath, "w",encoding="utf-8", newline='\n')

  for altered_line in altered_lines:
    f.write(altered_line)
  f.close()


  # If no model is specified, grab the newest
  if not model_name:
    models = list(model_folder_path.rglob("*.mod"))
    model = max(models, key=os.path.getctime)
  else:
    # Since the model will be recursively globbed to be found, remove any path/extension
    model_name = no_path_no_ext(model_name)
    model = next(model_folder_path.rglob(model_name + ".mod"))
  
  model = select_model(model_name)
  log('anystyle -P "' + model + '" -f json --stdout parse "' + filepath + '"')
  data = subprocess.check_output('anystyle -P "' + model + '" -f json --stdout parse "' + filepath + '"', stderr=subprocess.STDOUT, shell=True)
  log(data)
  data = json.loads(data)

  # Remove type field
  for citation in data:
    del citation["type"]

  return [
    # Put quotes around the parameters in case of space
    data,
    os.path.basename(model)
  ]

def no_path_no_ext(value):
  return os.path.splitext(os.path.basename(str(value)))[0]


"""
select_model is a function that'll return a model to use.
It'll make sure that .mod (the model extension) is added, and then
try to find the model. If the model exists, return the path of that model.
If the model doesn't exist, throw an exception

Example usage: select_model("examples-300.mod")
Example return: model/examples-300.mod
"""
def select_model(model_name):
  # Since the model will be recursively globbed to be found, remove any path/extension

  model_name = no_path_no_ext(model_name)
  try:
    model_path = str(next(model_folder_path.rglob(model_name + ".mod")))
  except StopIteration:
    models = list(model_folder_path.rglob("*.mod"))
    model_path = max(models, key=os.path.getctime)

  if os.path.isfile(model_path):
    return model_path
  else:
    raise FileNotFoundError

"""
train_model: use anystyle-cli's train method to train a new model

Note that this is mainly used internally from the /train and /retrain endpoints

Arguments: 
  > model_path: str. Path to model. This can be an existing you want to overwrite, or a non-existing one to make a fully new model
  > data_path: str. Path to the training data. This data (formatted in XML) will be used to train the model in question, and will be saved alongside it (for retraining, see retrain)
  > overwrite: bool. Whether to overwrite the existing model in case model_path points to one
  > input_filenames: iterable<str>, optional. The paths to files that have to be removed after everything's done

Example:
  Usage: train_model("year-models/1926-1950.mod", "year-models/1926-1950.mod.xml", True)
  return: str(anystyle-cli stdout)

"""
def train_model(model_path, data_path, overwrite, input_filenames=None):
  if input_filenames is None:
    input_filenames = []
  model_exists = os.path.exists(model_path)

  if model_exists:
    shutil.copy2(model_path, model_path + ".bak")
    input_filenames.append(model_path + ".bak")
  
  # Try to update the model
  try:
    if not overwrite and model_exists:
      return index_error(409, "Model already exists, and header 'overwrite' not set to True")
    elif overwrite and model_exists:
      os.remove(model_path)
  
    command = f'anystyle train "{data_path}" "{model_path}"'
    output = str(subprocess.check_output(command, shell=True))

    remove_in_background(input_filenames)

    return index_success(200, "Successfully updated model. Thank you for your contribution. Output: " + output)
  # On any crash, recover backup
  except Exception as e:
    log("Error during training")
    # Remove the new model if it exists
    if os.path.exists(model_path):
      os.remove(model_path)
    
    # Only try to recover if it exists
    if model_exists:
      shutil.copy2(model_path + ".bak", model_path)

    remove_in_background(input_filenames)
    return index_error(500, e)

"""
/train: pass a model name


Body:
  > a string, formatted in XML. See Anystyle documentation for more info

Headers:
  > model-name: str. The name of the model
  > overwrite: bool. Whether to overwrite the existing model in case model-name points to one
"""
@api.route('/train', methods=['POST'])
@api.route('/train-xml', methods=['POST'])
@api.route('/train/xml', methods=['POST'])
def train():
  model_name = request.headers.get("model-name")
  overwrite = header_boolean(request.headers.get("overwrite"), default=False)
  log(overwrite)

  input_filenames = []

  # Lowercase and secure model name
  model_name = model_name.lower().rstrip(".mod")

  model_path = model_folder + "/data/models/" + model_name + ".mod"
  data_path = model_path + ".xml"
  
  save_data(request, data_path)

  return train_model(model_path, data_path, overwrite, input_filenames)
    
"""
Training from CSV

@api.route('/train-csv', methods=['POST'])
def train_from_csv():
  input_csv = save_data_to_tmp(request, "csv")
  log(subprocess.check_output(f'python3 "{model_folder_path}/csv2xml.py" "{input_csv}" "{data_path}"', shell=True))
"""

# Serve CSS until it's handled by something else
@api.route('/css/<path:path>')
def css(path):
    return send_from_directory('css', path)

# And the same for assets
@api.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('assets', path)

# And the same for JS
@api.route('/js/<path:path>')
def js(path):
  return send_from_directory('js', path)

try:
  os.mkdir(temporary_folder)
except FileExistsError:
  pass

"""
Warning: Silently ignoring app.run() because the application is run from the flask command line executable. Consider putting 
app.run() behind an if __name__ == "__main__" guard to silence this warning.
"""
if __name__ == '__main__':
  api.run()
