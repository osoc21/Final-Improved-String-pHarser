# tester

# POST fish.com/ DATA --> return json

from flask import Flask, render_template, request
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
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Final-Improved-String-pHarser"
    }
)
api.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

temporary_folder = "temp/"
model_folder = "model/"
GROBID_PATH = "grobid_client_python/"

"""
User Interface to manually upload a file, or (later on) manually correct output.

URL: domain.com
METHOD: GET

---

An alias for /parse
URL: domain.com
METHOD: POST

"""
@api.route('/', methods=['GET', 'POST'])
def get_homepage():
    models = list(model_folder_path.rglob("*.mod"))

    if request.method == "GET":
        return render_template("index.html", models=get_all_models())

    # If a post gets done to /, assume the user wants to parse, so call /parse
    elif request.method == "POST":
        return parse()


@api.route('/about/', methods=['GET'])
def get_about_page():
    return render_template("about.html")


@api.route('/tos/', methods=['GET'])
def get_tos_page():
    return render_template("termsofuse.html")


@api.route('/contact/', methods=['GET'])
def get_contact_page():
    return render_template("contact.html")

def get_all_models():
  return list(model_folder_path.rglob("*.mod"))


def index_error(err_code, message):
  data = {"response": message, "type": "error"}
  return render_template('index.html', data=data, models=get_all_models()), err_code, {'Content-Type': 'text/html'}

def index_success(success_code, success_msg):
  data = {"response": success_msg, "type": "success"}
  return render_template('index.html', data=data, models=get_all_models()), success_code, {'Content-Type': 'text/html'}

def remove_in_background(filenames):
  if type(filenames) == str:
    filenames = [filenames] 
  threading.Thread(target=remove_files, args=(filenames,)).start()  # , is important

"""
save_data_to_file uses its parameters to save the POST data to a random filename,
returning the filename afterwards

request: the request object
ext: the extension to save the file as
form_input_name: the name of the form input to get data from
"""
# Pass the request object,  the extension and 
def save_data_to_tmp(request, ext,  form_input_name=None):
  print("request")

  print(request)
  # To ensure no duplicate filenames, use headers to create a filename
  # This will give issues if two people upload two files with the exact same size on the exact same second
  # This should do the trick for now, but it can be changed later on to a more heavyweight solution if need be
  temp_filename = temporary_folder + request.headers.get("content-length") + time.strftime("%Y%m%d%H%M%S") + "." + ext
  return save_data(request, temp_filename, form_input_name)

def save_data(request, filename, form_input_name=None):
  # If a string was directly given (no direct file upload), save it to a file
  if len(request.files) <= 0:
    # https://stackoverflow.com/a/42154919  https://stackoverflow.com/a/16966147
    # Either get from form or from request data
    data = request.form.get(form_input_name, request.get_data().decode("utf-8"))
    file_from_string = open(filename, "w", encoding="utf-8")
    file_from_string.write(data)
    file_from_string.close()
  else:
    # If a file is getting uploaded, save it as well
    request.files['file'].save(filename)
  return filename


"""
Parse citation strings from plain text, with one citation per line. This is the most ideal method

URL: domain.com/parse
Method: POST
Content-Type: text/plain

---

Parse citation strings from a csv string into an array of JSON objects.

URL: domain.com/parse
Method: POST
Headers:
  Content-Type: text/csv
  Ignore-Firstline: {boolean, optional, defaults to True}
    (
      Ignore the firstline. Set to true if first line is a header, for example,: String,Authors,Year...
      Valid values: false, False, true, True, 1, 0
    )
  Single-Column: {int, optional, defaults to -1}
    (
      Only keep the data in the column with index int
      Won't have effect if not set
      Example situation: a csv file with Citationstring,Authors,Year,Title,Book --> use index 0
    )

---

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
CITATION_STRING_CONST = "citationstring"
# Currently only support from form
@api.route('/retrain', methods=['POST'])
def retrain():
  model_name = request.form["model"]

  print(model_name)

  model_path = select_model(model_name)
  model_data_path = model_path + ".xml"
  model_data = ET.parse(model_data_path)

  dataset = model_data.getroot()
  sequence = ET.SubElement(dataset, "sequence")

  keys = request.form.keys()
  for key in keys:
    print(key)
    # Don't add model-name to XML
    if key == "model-name":
      continue

    value = request.form[key]
    print("  " + value)

    
    ET.SubElement(sequence, key).text = value

    
  
  model_data.write(model_data_path)

  print("training")
  train_model(model_path, model_data_path, overwrite=True)
  print("trained")

  #if request.form:
    # TODO: retrain model here
  return index_success(200, "Successfully updated model. Thank you for your contribution")

def process_pdf_file(file_path):
  path = os.path.dirname(file_path)
  path = ''.join(path)
  file_name = file_path.split("/")[len(file_path.split("/")) - 1]
  #subprocess.check_output('python3 ./hello.py', shell=True)
  data = subprocess.check_output('python3 grobid_client_python/example.py' + ' ' + path + ' ' +
                                 file_name, shell=True)
  print("data")

  print(data)
  return data

def parse_pdf():
  #model_name = request.headers.get("model-name")
  input_filename = GROBID_PATH + temporary_folder + request.files['file'].filename
  data = process_pdf_file(input_filename)#, model_name)
  print(input_filename)
  return_data = {
    "data": data,
    "original_strings": ""
  }
  return render_template("response.html", data=return_data)

@api.route('/parse', methods=['POST'])
def parse():
  # Step 1: figure out what kind of input is given
  content_type = request.headers.get("content-type")

  if "multipart/form-data" in content_type:
    input_type = "form"
  elif "text/plain" in content_type:
    input_type = "txt"
  elif "csv" in content_type:
    input_type = "csv"
  elif "pdf" in content_type:
    input_type = "pdf"

  # If a form is used to send a file
  if len(request.files) >= 1:
    old_filename = request.files['file'].filename.lower()
    # Check for allowed formats
    if old_filename.endswith("csv"):
      input_type = "csv"
    elif old_filename.endswith("txt") or old_filename.endswith("ref"):
      input_type = "txt"
    elif old_filename.endswith("pdf"):
      input_type = "pdf"
    else:
      # If a non-supported format gets uploaded, return 422
      return index_error(422, "The uploaded file format (" + old_filename[old_filename.rfind("."):] + ") isn't supported.")
  # If input type couldn't be determined, assume plaintext
  else:
    input_type = "txt"

  # Step 2: put the input in a form that anystyle-cli can work with
  """
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


  From the documentation we can conclude that a .txt (or a .ref file) with one citation per line is suitable for input
  """
  
  input_filename = save_data_to_tmp(request, input_type, CITATION_STRING_CONST)
  input_filenames = [input_filename]  # List of filenames to clean later

  """ 
  Example of a line as provided in a .csv file by VLIZ:
  Krohling, W., & Zalmon, I. R. 2008. Epibenthic colonization on an artificial reef in a stressed environment off the north coast of the Rio de Janeiro State, Brazil. Brazilian Archives of Biology and Technology 51: 213-221.
  """
  if input_type == "pdf":
    return parse_pdf()

  if input_type == "csv":
    input_filename_csv = input_filename
    input_filename = input_filename_csv.replace("csv", "txt")
    input_filenames.append(input_filename)

    ignore_firstline = header_boolean(request.headers.get("Ignore-Firstline"), default=True)
    single_column = header_int(request.headers.get("Single-Column"), default=-1)

    with open(input_filename_csv, "r", encoding="utf-8") as original_csv:
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
      with open(input_filename, "w", encoding="utf-8") as input_file:
        input_file.writelines(csv_data)


  # Step 3: run anystyle and return the result
  model_name = request.form["model-name"] or request.headers.get("model-name")
  data, used_model = process_file(input_filename, model_name)

  original_strings = []
  with open(input_filename, "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
      original_strings.append(line.strip("\n"))

  remove_in_background(input_filenames)

  """
  if request.form and CITATION_STRING_CONST not in request.form:
    # TODO: retrain model here
    return index_success(200, "Successfully updated model. Thank you for your contribution")
  """

  if len(data) <= 0:
      return index_error(422, "No data found in input")

  print("Returning data...")
  return_data = {
    "model": used_model,
    "data": data,
    "original_strings": original_strings
  }
  return render_template("response.html", data=return_data, model=used_model)
  

def remove_files(files):
  try:
    for file in files:
      os.remove(file)
    print("Removed")
  except Exception as e:
    print("Error while removing")
    print(e)


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
  f = open(filepath, "r")
  altered_lines = []
  for line in f.readlines():
    altered_line = line.replace("\"", "")
    altered_lines.append(altered_line)
  f = open(filepath, "w")

  for altered_line in altered_lines:
    f.write(altered_line)

  # If no model is specified, grab the newest
  if not model_name:
    models = list(model_folder_path.rglob("*.mod"))
    model = max(models, key=os.path.getctime)
  else:
    # Since the model will be recursively globbed to be found, remove any path/extension
    model_name = no_path_no_ext(model_name)
    model = next(model_folder_path.rglob(model_name + ".mod"))
  
  # rglob may return WindowsPath, so convert to str
  model = str(model)
  data = subprocess.check_output('anystyle -P "' + model + '" -f json --stdout parse "' + filepath + '"', shell=True)
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
  return os.path.splitext(os.path.basename(value))[0]


"""
select_model is a function that'll return a model to use.
It'll make sure that .mod (the model extension) is added, and then
try to find the model. If the model exists, return the path of that model.
If the model doesn't exist, throw an exception

Example usage: select_model("examples-300.mod")
Example return: model/examples-300.mod
"""
def select_model(model_name):
  print(model_name)
  model_name = model_name.rstrip(".mod")
  model_path = str(next(model_folder_path.rglob(model_name + ".mod")))

  if os.path.isfile(model_path):
    return model_path
  else:
    raise FileNotFoundError

def train_model(model_path, data_path, overwrite, input_filenames=[]):
  model_exists = os.path.exists(model_path)

  if model_exists:
    shutil.copy2(model_path, model_path + ".bak")
    input_filenames.append(model_path + ".bak")
  
  # Try to update the model
  try:
    if not overwrite and model_exists:
      return index_error(403, "Model already exists, and header 'overwrite' not set to True")
    elif overwrite and model_exists:
      pass
      
    if overwrite and model_exists:
      # TODO APPEND!!
      os.remove(model_path)
  

    command = f'anystyle train "{data_path}" "{model_path}"'
    print(command)
    output = subprocess.check_output(command, shell=True)

    remove_in_background(input_filenames)

    return output
  # On any crash, recover backup
  except Exception as e:
    print("Error during training")
    # Remove the new model if it exists
    if os.path.exists(model_path):
      os.remove(model_path)
    
    # Only try to recover if it exists
    if model_exists:
      shutil.copy2(model_path + ".bak", model_path)

    remove_in_background(input_filenames)
    return index_error(500, e)


#train_and_check = str(next(model_folder_path.rglob("train_and_check.sh")))
@api.route('/train', methods=['POST'])
def train():
  content_type = request.headers.get("content-type")
  model_name = request.headers.get("model-name")
  overwrite = header_boolean(request.headers.get("overwrite"), default=False)

  input_filenames = []

  # Lowercase and secure model name
  model_name = model_name.lower().rstrip(".mod")

  model_path = model_folder + "/data/models/" + model_name + ".mod"
  data_path = model_path + ".xml"

  if "csv" in content_type:
    input_type = "csv"
    input_csv = save_data_to_tmp(request, input_type)
    print(subprocess.check_output(f'python3 "{model_folder_path}/csv2xml.py" "{input_csv}" "{data_path}"', shell=True))

    input_filenames.append(input_csv)
  
  save_data(request, data_path)

  train_model(model_path, data_path, overwrite, input_filenames)
  


# Serve CSS until it's handled by something else
@api.route('/css/<path:path>')
def css(path):
    return send_from_directory('css', path)


# And the same for assets
@api.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('assets', path)


@api.route('/js/<path:path>')
def js(path):
  return send_from_directory('js', path)



# Upload citation string
'''@api.route('/', methods=['POST'])
def post_data():
  print("POSTINGGG")
  if request.files.get('data_file'):
    f = request.files['data_file']
  print(f)
  stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
  csv_input = csv.reader(stream)
    #print("file contents: ", file_contents)
    #print(type(file_contents))
  print(csv_input)
  for row in csv_input:
    print(row)

  return render_template("index.html")'''

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
