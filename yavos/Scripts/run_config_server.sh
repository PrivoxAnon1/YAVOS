source ../venv_yavos/bin/activate
export PYTHONPATH=$PWD
cd Config
python -W ignore -m http.server --cgi

