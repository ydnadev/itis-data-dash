# ITIS Data Dash

Simple dashboard of taxonomic data sourced from ITIS [[1]](#1).
Dashboard: https://ydnadev-itis-data-dash-itis-data-dash-mmsio8.streamlit.app/

## Usage

*Note - ITIS database does not exist in this repository, download ITIS data from source below.* 

Extract data from ITIS SQLite db  
    - run src/script1.sql to dump data for all species to *itisdata/animal_species.txt*  
    - run rc/script2.sql to dump data for all taxa hierarchy to *itisdata/animal_taxa.csv*  

Parsing assumes 2 files above- 
```bash
perl src/itis_parser.pl 
```

Dashboard -
```bash
streamlit run itis_dash.py
```
## References
<a id="1">[1]</a> 
Retrieved from the Integrated Taxonomic Information System (ITIS) on-line database, www.itis.gov, CC0
https://doi.org/10.5066/F7KH0KBK
