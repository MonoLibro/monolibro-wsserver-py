#!/usr/bin/bash
python3 monolibro.py
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf