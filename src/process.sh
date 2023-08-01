#! /bin/bash
# batch run scripts
sqlite3 ../itisdata/ITIS.sqlite < script1-species.sql
sqlite3 ../itisdata/ITIS.sqlite < script1-subspecies.sql
sqlite3 ../itisdata/ITIS.sqlite < script2-species.sql
sqlite3 ../itisdata/ITIS.sqlite < script2-subspecies.sql
sqlite3 ../itisdata/ITIS.sqlite < script3-vernacular.sql
sqlite3 ../itisdata/ITIS.sqlite < script4-geographic.sql
for file in ../itisdata/*.csv
do 
    vi +':w ++ff=unix' +':q' "$file"
done
for file in ../itisdata/*.txt
do 
    vi +':w ++ff=unix' +':q' "$file"
done
perl itis_parser.pl
python3 itis_parq_convert.py
