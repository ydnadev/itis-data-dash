/* file: species.txt tab sep */
/* find all species level data */
select tu.*
from taxonomic_units tu
where tu.rank_id in ('220') --species
    --and tu.kingtom_id = '5' --animalia
order by tu.tsn
;
