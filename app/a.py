# tester

# POST fish.com/ DATA --> return json

from flask import Flask, render_template, request
import subprocess

api = Flask(__name__)


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
            new_filename = "tmp/" + f.filename
            f.save(new_filename)

            data = subprocess.check_output('anystyle -f json --stdout parse ' + new_filename, shell=True)
            return api.response_class(
                response=data,
                status=200,
                mimetype='application/json'
            )
        else:
            print("no data file")

        return render_template("index.html")


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

if __name__ == '__main__':
    api.run()
