.headers on
.mode csv
.output ../itisdata/geographic.csv
/* file: geographic.csv */
select g.tsn
    ,g.geographic_value
from geographic_div g
;
.output stdout
