# tester
import requests
base_url = "localhost:3000/"

# POST fish.com/ DATA --> return json

#response = requests.get(base_url)
#print(response)


from flask import Flask, json, render_template, request

companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]

api = Flask(__name__)

@api.route('/', methods=['GET', 'POST'])
def get_homepage():
  if request.method == "GET":
    return render_template("index.html")
  elif request.method == "POST":
    if request.files.get('file'):
      print("found file")
      f = request.files['file']
      print(f)
      stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
      csv_input = csv.reader(stream)
          #print("file contents: ", file_contents)
          #print(type(file_contents))
      print(csv_input)
      for row in csv_input:
        print(row)
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
