# tester

# POST fish.com/ DATA --> return json

from flask import Flask, render_template, request
from flask_swagger_ui import get_swaggerui_blueprint
import subprocess
import os
import shutil
import glob
import time
import csv
import json

from flask.helpers import send_from_directory

api = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Seans-Python-Flask-REST-Boilerplate"
    }
)
api.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

temporary_folder = "temp/"
model_folder = "model/"


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
    if request.method == "GET":
        return render_template("index.html")

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
@api.route('/parse', methods=['POST'])
def parse():
  # Step 1: figure out what kind of input is given
  content_type = request.headers.get("content-type")
  file_upload = False
  
  if "text/plain" in content_type:
    input_type = "txt"
  if "csv" in content_type:
    input_type = "csv"
  # If a form is used to send a file
  elif "multipart/form-data" in content_type:
    file_upload = True
    old_filename = request.files['file'].filename.lower()
    # Check for allowed formats
    if old_filename.endswith("csv"):
      input_type = "csv"
    elif old_filename.endswith("txt") or old_filename.endswith("ref"):
      input_type = "txt"
    else:
      # If a non-supported format gets uploaded, return 422
      return api.response_class(
          response="The uploaded file format (" + old_filename[old_filename.rfind("."):] + ") isn't supported.",
          status=422  # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422
      )
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
  
  # To ensure no duplicate filenames, use headers to create a filename
  # This will give issues if two people upload two files with the exact same size on the exact same second
  # This should do the trick for now, but it can be changed later on to a more heavyweight solution if need be
  input_filename = temporary_folder + request.headers.get("content-length") + time.strftime("%Y%m%d%H%M%S") + "." + input_type
 
  # If a string was directly given, save it to a file
  if not file_upload:
    file_from_string = open(input_filename, "w", encoding="utf-8")
    file_from_string.write(request.get_data().decode("utf-8"))
    file_from_string.close()
  else:
    # If a file is getting uploaded, save it as well
    request.files['file'].save(input_filename)
  

  """ 
  Example of a line as provided in a .csv file by VLIZ:
  Krohling, W., & Zalmon, I. R. 2008. Epibenthic colonization on an artificial reef in a stressed environment off the north coast of the Rio de Janeiro State, Brazil. Brazilian Archives of Biology and Technology 51: 213-221.
  """

  if input_type == "csv":
    input_filename_csv = input_filename
    input_filename = input_filename_csv.replace("csv", "txt")

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
  model_name = request.headers.get("model-name")
  data, used_model = process_file(input_filename, model_name)

  # TODO remove the old file, but can it be done asynchronously?


  return {
    "model": used_model,
    "data": json.loads(data)
  }



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
def process_file(filepath, model_name=False):
  # If no model is specified, grab the newest
  if not model_name:
    models = glob.glob(model_folder + "*.mod")
    model = max(models, key=os.path.getctime)
  else:
    model = select_model(model_name)
  return [
    subprocess.check_output('anystyle -P ' + model + ' -f json --stdout parse ' + filepath, shell=True),
    model.replace(model_folder, "")
  ]



"""
select_model is a function that'll return a model to use.
It'll make sure that .mod (the model extension) is added, and then
try to find the model. If the model exists, return the path of that model.
If the model doesn't exist, throw an exception

Example usage: select_model("examples-300.mod")
Example return: model/examples-300.mod
"""
def select_model(model_name):
  # Ensure that model_path has the folder & extension, but only once
  model_name = model_name.replace(model_folder, "").replace(".mod", "")
  model_path = model_folder + model_name + ".mod"

  if os.path.isfile(model_path):
    return model_path
  else:
    raise FileNotFoundError



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
