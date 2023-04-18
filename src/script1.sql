/* find all animal species level data */
select tu.*
from taxonomic_units tu
where tu.rank_id in ('220') --species, '230' --subspecies
    and tu.kingtom_id = '5' --animalia
order by tu.tsn
;
