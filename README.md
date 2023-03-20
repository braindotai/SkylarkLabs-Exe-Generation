# SkylarkLabs.ai Server Exe

## Setup Guide

```
$ python -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
``` 
- Put your model in assets/models folder, and rename it to random file name, for example - `config.system.abc`
- Use same model file name as `config.system.abc` in your `server.py`.

## Producing Exe

Note that `pyinstaller` must be installed in your local virtual environment otherwise the generated exe would be bigger file in GBs since it would consider all global dependencies in your system.

Simply install eveything by using the `requirements.txt`, and all should be fine.

```
$ pyinstaller --clean --onefile --console --icon <path to icon file> --name <your exe name> --add-data "assets/models/model.onnx;." "server.py"
```
