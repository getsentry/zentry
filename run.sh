#!/usr/bin/env bash

# exit on first error
set -xe

reset 

# create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install (or update) requirements
python -m pip install -r zentry/requirements.txt

# Run app
cd zentry && python main.py && cd ..