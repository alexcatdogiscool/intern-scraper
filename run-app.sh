#!/bin/bash

cd /home/alex/Desktop/programming/internship-scraper

source ./.venv/bin/activate

flask --app backend run --host 0.0.0.0

deactivate
