#!/usr/bin/env bash

source .venv/bin/activate
pip freeze | sed "s/.*mkdocs-to-pdf.*/\.\.\/\.\.\//g" > requirements-full.txt
