#!/usr/bin/bash
python3 monolibro.py -d
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf