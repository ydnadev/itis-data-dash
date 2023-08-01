.headers on
.mode csv
.output ../itisdata/species_vernacular.csv
/* file: species_vernacular.csv */
/* export vernacular (common names) */
select tu.tsn, tu.complete_name, v.vernacular_name
from vernaculars v 
    inner join taxonomic_units tu
        on v.tsn = tu.tsn
            --and tu.kingdom_id = '5'
order by v.vernacular_name
;
.output stdout
