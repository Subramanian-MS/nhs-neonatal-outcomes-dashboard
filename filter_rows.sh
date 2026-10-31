#!/bin/bash
# Filters official NHS England Maternity Services Data Set (MSDS) and Data Quality CSV files
# to the 24 benchmarked Level 3 NICU Trusts (by NHS ODS Trust code).
# Usage: ./filter_rows.sh
HERE=$(pwd)
python3 "$HERE/generate_source_data.py" "$HERE"
