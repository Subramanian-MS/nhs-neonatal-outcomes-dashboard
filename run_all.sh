#!/bin/bash
# Rebuilds the NHS Neonatal Intensive Care Outcomes & Data Quality dashboard from the official NHS England MSDS & Data Quality CSV releases.
# Usage: ./run_all.sh
# Optional: LATEST_YEAR="2024/25" ./run_all.sh
set -e
HERE=$(pwd)
python3 "$HERE/generate_source_data.py" "$HERE"
mkdir -p work && cd work && mkdir -p flt out dash
python3 "$HERE/clean.py"
python3 "$HERE/dims.py" >/dev/null
python3 "$HERE/dropzeros.py"
python3 "$HERE/dash.py"            # headline-slice tables (Dash_*.csv) + dash/data.json
python3 "$HERE/ext.py"             # + per-unit 5-year trends & clinical breakdown -> dash/data2.json
python3 "$HERE/extend.py"          # + MSDS data item completeness & gestation bands per unit -> dash/data3.json
python3 "$HERE/validate.py" flt dash/data3.json "$HERE/docs/Validation_Report.md" out/Dim_Unit.csv
python3 "$HERE/build_html.py" "$HERE/template/dashboard_template.html" dash/data3.json "$HERE/docs/Validation_Report.md" "$HERE/NHS_Neonatal_Dashboard.html"
cp "$HERE/NHS_Neonatal_Dashboard.html" "$HERE/index.html"
echo "Done. Dashboard: NHS_Neonatal_Dashboard.html (and index.html)   Power BI tables: work/dash/*.csv   Checks: docs/Validation_Report.md"
