# tester

# POST fish.com/ DATA --> return json

from flask import Flask, render_template, request
from flask_swagger_ui import get_swaggerui_blueprint
import subprocess
import os
import shutil

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


@api.route('/', methods=['GET', 'POST'])
def get_homepage():
    if request.method == "GET":
        return render_template("index.html")

    elif request.method == "POST":
        # Check if a file was uploaded (key name: file)
        if request.files.get('file'):
            f = request.files['file']

            # It seems like anystyle-cli wants a file to read, and can't handle a direct string input,
            # but keeping the following line commented in case we find a way to direct it
            # stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)

            # Save the uploaded file
            new_filename = temporary_folder + f.filename
            f.save(new_filename)

            data = subprocess.check_output('anystyle -f json --stdout parse ' + new_filename, shell=True)
            return api.response_class(
                response=data,
                status=200,
                mimetype='application/json'
            )
        else:
            new_filename = temporary_folder + "citation.txt"
            f = open(new_filename, "w")
            f.write(request.form.get("data"))
            f.close()
            data = subprocess.check_output('anystyle -f json --stdout parse ' + new_filename, shell=True)
            return api.response_class(
                response=data,
                status=200,
                mimetype='application/json'
            )

        return render_template("index.html")


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
