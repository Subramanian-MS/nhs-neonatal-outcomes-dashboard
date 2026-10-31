#!/bin/bash
# Rebuilds the NHS Neonatal Outcomes & BadgerNet Data Quality dashboard from the raw NNAP/BadgerNet zip.
# Usage: ./run_all.sh /path/to/NNAP_BadgerNet_Extract.zip
# Optional: LATEST_YEAR="2024/25" ./run_all.sh ...   (when a new annual audit extract is published)
set -e
ZIP=$(realpath "$1"); HERE=$(pwd); mkdir -p work && cd work && mkdir -p raw flt out dash
unzip -q -o "$ZIP" -d raw
for t in 1 5 6 8 22 26 28; do bash "$HERE/filter_rows.sh" $t; python3 "$HERE/clean.py" $t; done
python3 "$HERE/dims.py" >/dev/null
python3 "$HERE/dropzeros.py"
python3 "$HERE/dash.py"            # headline-slice tables (Dash_*.csv) + dash/data.json
python3 "$HERE/ext.py"             # + per-unit 7-year trends & episode breakdown -> dash/data2.json
python3 "$HERE/extend.py"          # + clinical audit measures & gestation bands per unit -> dash/data3.json
python3 "$HERE/validate.py" flt dash/data3.json "$HERE/docs/Validation_Report.md" out/Dim_Unit.csv
python3 "$HERE/build_html.py" "$HERE/template/dashboard_template.html" dash/data3.json "$HERE/docs/Validation_Report.md" "$HERE/NHS_Neonatal_Dashboard.html"
cp "$HERE/NHS_Neonatal_Dashboard.html" "$HERE/index.html"
echo "Done. Dashboard: NHS_Neonatal_Dashboard.html (and index.html)   Power BI tables: work/dash/*.csv   Checks: docs/Validation_Report.md"
