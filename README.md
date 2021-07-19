# Final-Improved-String-pHarser

## About
...

## Installation

### Docker
After installing Docker, all you have to do is build the dockerfile:
```bash
$ sudo docker build -t fish .
```

### Manual
- `git clone https://github.com/osoc21/Final-Improved-String-pHarser.git`
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
docker run -p 5000:5000 --mount type=bind,src="$(pwd)/app",target=/app --mount type=bind,src="$(pwd)/model",target=/app/model fish 
```


## Credits
...

## License
...
