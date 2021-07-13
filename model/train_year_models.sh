export YEARS_MODEL_PATH="year_models"
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --end 1850 --out $YEARS_MODEL_PATH/0-1850.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 1851 --end 1900 --out $YEARS_MODEL_PATH/1851-1900.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 1901 --end 1925 --out $YEARS_MODEL_PATH/1901-1925.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 1926 --end 1950 --out $YEARS_MODEL_PATH/1926-1950.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 1951 --end 1960 --out $YEARS_MODEL_PATH/1951-1960.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 1961 --end 1970 --out $YEARS_MODEL_PATH/1961-1970.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 1971 --end 1980 --out $YEARS_MODEL_PATH/1971-1980.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 1981 --end 1990 --out $YEARS_MODEL_PATH/1981-1990.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 1991 --end 2000 --out $YEARS_MODEL_PATH/1991-2000.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 2001 --end 2010 --out $YEARS_MODEL_PATH/2001-2010.mod
python3 train_and_accuracy.py ${1:-examples-2251.csv} 0.7 --start 2011 --end 2021 --out $YEARS_MODEL_PATH/2011-2021.mod