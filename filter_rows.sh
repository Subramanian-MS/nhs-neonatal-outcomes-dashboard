#!/bin/bash
# Filters raw NNAP / BadgerNet extract tables to the 24 benchmarked Level 3 NICUs (by NHS ODS Trust code).
# Usage: ./filter_rows.sh <table_number>
t=$1
ROOT=$(pwd); cd "$ROOT/raw/NNAP_Extract"
PAT='^(\xef\xbb\xbf)?(RR8|RHQ|RAE|RWA|RJ1|RRV|RJZ|RYJ|RJ7|RQX|R0A|REP|RXN|RTD|RTR|RGT|RM1|RTH|RHM|RVJ|RA7|RQ3|RKB|RX1),'
for f in $(unzip -Z1 table-$t.zip); do
  y=$(echo $f | sed -E 's/.*-([0-9]{4}-[0-9]{2})\.csv/\1/')
  ( unzip -p table-$t.zip $f | tr -d '\r' | awk -v pat="$PAT" 'BEGIN{h=0} { if(!h){ if($0 ~ /^ODS_Code,/ || $0 ~ /^\xef\xbb\xbfODS_Code,/){print; h=1} } else if ($0 ~ pat) print }' ) > "$ROOT/flt/table-$t-$y.csv"
done
echo done $t
