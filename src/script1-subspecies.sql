.headers on
.mode csv
.separator "\t"
.output ../itisdata/subspecies.txt
/* file: subpecies.txt tab sep */
/* find all species level data */
select tu.*
from taxonomic_units tu
where tu.rank_id in ('230') --subspecies
    --and tu.kingtom_id = '5' --animalia
order by tu.tsn
;
.output stdout
