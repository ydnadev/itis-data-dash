# ITIS Data Dash

Simple dashboard of taxonomic data sourced from ITIS [[1]](#1).

## Usage

*Note - ITIS database does not exist in this repository, download ITIS data from source below.* 

Extract data from ITIS SQLite db  
    - run SQL script 1 to dump data for all species to *animal_species.txt*  
    - run SQL script 2 to dump data for all taxa hierarchy to *animal_taxa.csv*  

Parsing assumes 2 files above- 
```bash
perl itis_parser.pl 
```

Dashboard -
```bash
streamlit run itis_dash.py
```
## References
<a id="1">[1]</a> 
Retrieved from the Integrated Taxonomic Information System (ITIS) on-line database, www.itis.gov, CC0
https://doi.org/10.5066/F7KH0KBK
