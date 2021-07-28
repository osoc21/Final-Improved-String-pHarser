# Final-Improved-String-pHarser

## About
The Final Improved String pHarser (FISH) has been made during Open Summer of Code 2021, this project is dedicated to split a scientific reference into its relevant components and return the result as a downloadable json file.
The current features available include: parsing a single reference, parsing a file of references (see "example data" under "app" for valid formats), and extracting references from a pdf.
These features are based on already available open source projects and integrate/combine functionalities of these alternatives.   
The first two features are mainly build with the code of [Anystyle.io](https://anystyle.io/), which provides one of the best services for this purpose.
Instead of using their default model however, the model behind FISH is trained on data provided by the flemish marine institute, consisting of around 2000 example
references with no fixed format, going back to the mid 18th century.   
There are currently 3 models available, these models are trained on differenct datasets, which can be found under model/data/csv/.
The aphiaFull (dataset = ahiaTrainingset.csv) model is trained on more fields, while the dataset of the normal aphia model and allExamples.mod only provide limited labels in which a new reference can be parsed.
For the estimated accuracy of the models one can run the Train_and_accuracy.py file under model, this file accepts a csv file with a full string and the parsed solution (see data under model for example input files),
it trains a model on a fraction of the input file and tests the model on the remaining entries, as a result it displays the error rate: the rate where the output of the model differs from the correct answer in the input file.
For more information, see the anystyle documentation: https://github.com/inukshuk/anystyle     
For the last service, reading references from pdf, [Grobid](https://grobid.readthedocs.io/en/latest/) is used. 
Although they do not allow manual training, their service is high quality and well documented.

## Installation

### Docker
NOTE: for some reason, Docker on a windows host gave issues for parsing. If you're getting an ioctl/jsondecode error, do the good old Windows > WSL > Docker

After installing Docker, all you have to do is build the dockerfile:
```bash
$ sudo docker build -t fish .
```

### Manual
- `git clone https://github.com/osoc21/Final-Improved-String-pHarser.git`
- Run `git submodule update --init --recursive`
- Install Python3 and Ruby
- Install dependencies
    - `gem install anystyle-cli`
    - `pip install -r requirements.txt` (in the main directory of FISH)

<br>

## Usage

### Docker
Run the following command:
```bash
$ sudo docker run -p 5000:5000 fish
```

### Manual (Windows)
```
set FLASK_APP=app/a.py
set FLASK_ENV=development
set FLASK_DEBUG=1
flask run
```

### Manual (Unix)
(In the root directory of FISH)
```
export FLASK_APP=app/a.py
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

<br>

## Contributing
### Python changes
If you've added any modules/packages, I recommend using [pipreqs](https://pypi.org/project/pipreqs/) to automatically update the requirements.txt. Simply run `pipreqs --force` before committing and you're done!

Docker with mounting:
```bash
docker run -p 5000:5000 --mount type=bind,src="$(pwd)/app",target=/app --mount type=bind,src="$(pwd)/model",target=/app/model --mount type=bind,src="$(pwd)/temp",target=/app/temp fish 
```

### Hook into existing Docker(-Compose) container

```bash
sudo docker ps
sudo docker exec -it <container name> /bin/bash 
```

## Credits
The credits of this code go to:
Felix Cammaerts, Stijn 'Cat' Catry and Maarten Wens   
Coached by: Chris Leroy and Liesbeth Lyssens

## License
The licence can be found in [LICENSE.txt](https://github.com/osoc21/Final-Improved-String-pHarser/blob/master/LICENSE.txt).
