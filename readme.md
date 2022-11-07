<p align="center" style="background-color: #003364;">

<img src="https://i.imgur.com/hRfS8Q2.png" alt="drawing" style="width:50%"/>
</p>
## Running

You can use the [already built binaries](https://github.com/Christian-Klempau/OpenVerbum/tree/main/executables), just double click the file.

You can execute the python script yourself. See [execute from source](#execute-from-source).

You can build it yourself. See [build from source](#build-from-source).

## Set up - Virtual environment

You need pipenv: `pip install pipenv`

- Install the env in your mashine: `pipenv install`

- Execute and enter the env shell on your terminal: `pipenv shell`

- Add a library to the env: `pipenv install {library}`

## Execute from source

Once you have your virtual environment installed and your terminal is inside it:

- `python main.py`

## Build from source

You need `PyInstaller`, `python 3.10` and the virtual environment set up.
There is a bug with `PyQt==5.15` and PyInstaller with the library `PyQt5.sip`. That's why we use `PyQt==5.14.X`.

- Linux: `bash build.sh`

- Windows: TODO

- MacOS: TODO

The built executable will be in `dist/OpenVerbum`.


## TODO: Make these executables

- MacOS binaries
- Windows binaries
