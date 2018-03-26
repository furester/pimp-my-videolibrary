# pimp-my-videolibrary
Find duplicates in a videolibrary and chose which one to keep based on meta

## Development

For development I suggest use of `virtualenv`.

`virtualenv` is a tool to create isolated Python environments. Why is this good?
You can create a new Python environment to run a Python/Django/whatever app and
install all package dependencies into the virtualenv without affecting your
system’s site-packages.

After cloning the project:

    cd pimp-my-videolibrary
    virtualenv --python=/usr/bin/python2.7 .

    source bin/activate
    bin/pip install -r requirements.txt
    python setup.py install
    bin/pip install -e .

## Usage

The setup script will install the program as `pimp`. You can invoke it using:

    bin/pimp

and get the help with

    bin/pimp --help

`pimp` uses a YAML based configuration file. The following example will look in
`/tmp` folder, will match any item that match extensions array:

    start_path: /tmp/
    extensions:
      - .pdf
      - .txt
