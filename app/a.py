# tester

# POST fish.com/ DATA --> return json

from flask import Flask, render_template, request
from flask_swagger_ui import get_swaggerui_blueprint
import subprocess
import os
import shutil
import glob

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
Parse citation strings into an array of JSON objects.

URL: domain.com/parse
Method: POST
Content-type: 


"""
@api.route('/parse', methods=['POST'])
def parse():
  # Check if a file was uploaded (key name: file)
  if request.files.get('file'):
      f = request.files['file']
      # Save the uploaded file
      new_filename = temporary_folder + f.filename
      f.save(new_filename)

      data, used_model = process_file(new_filename)
      return api.response_class(
          response=data,
          status=200,
          mimetype='application/json'
      )
  else:
      new_filename = temporary_folder + "citation.txt"
      f = open(new_filename, "w")

      f.write(request.get_data().decode("UTF8"))
      f.close()
      data, used_model = process_file(new_filename, model_name="examples-26")
      return api.response_class(
          response=data,
          status=200,
          mimetype='application/json'
      )



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
