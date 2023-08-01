.headers on
.mode csv
.output ../itisdata/taxa-species.csv
/* file: taxa-species.csv */
/* export all animal taxa */
select tu.tsn
    ,tu.unit_name1
    ,tu.parent_tsn
    ,tu.rank_id
from taxonomic_units tu
where tu.rank_id not in ('220','230') --species, subspecies
    --and tu.kingdom_id = '5' --animals, remove if desired
order by tu.tsn
;
.output stdout
