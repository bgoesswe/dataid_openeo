# openeo-python-client

Python client API for OpenEO. Allows you to interact with OpenEO backends from your own environment.

[![Status](https://img.shields.io/badge/Status-proof--of--concept-yellow.svg)]()

## Requirements

* Python 3.5
* Pip3

Windows users: It is recommended to install Anaconda Python as shapely may need to be installed separately using the Anaconda Navigator.

## Usage
[Examples and all use cases in python code](https://github.com/bgoesswein/dataid_openeo/tree/master/openeo-python-client/examples)

[General Unit tests](https://github.com/bgoesswein/dataid_openeo/tree/master/openeo-python-client/tests)

## Development

Installing locally checked out version:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```
Building the documentation:

As HTML:
```bash
python setup.py build_sphinx -c docs
 ```
As Latex: 
```bash
python setup.py build_sphinx -c docs -b latex
```
