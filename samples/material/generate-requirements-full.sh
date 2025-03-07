#!/usr/bin/env bash

source .venv/bin/activate
pip freeze | sed "s/.*mkdocs-with-pdf.*/\.\.\/\.\.\//g" > requirements-full.txt
