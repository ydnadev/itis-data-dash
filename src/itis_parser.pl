#! /usr/bin/perl
#
#use warnings;
use strict;

my $species = "../itisdata/species.txt";
my $species_sub = "../itisdata/subspecies.txt";
my $taxa = "../itisdata/taxa-species.csv";
my $taxa_sub = "../itisdata/taxa-subspecies.csv";
my $outfile_temp = "../itisdata/species_temp.txt";
my $outfile = "../itisdata/species_taxa.txt";
my $lcp = 0;
my %pars;
my %pars_sub;
my %tax;
my %tax_sub;
my @d;

# read tab separated species.txt from ITIS
open (SP, "<$species") || print "can\'t open species\n";
my @data_species = <SP>;
close SP;

# read tab separated subspecies.txt from ITIS
open (SUB, "<$species_sub") || print "can\'t open subspecies\n";
my @data_subspecies = <SUB>;
close SUB;

# read csv separated taxa.csv from ITIS
open (TSP, "<$taxa") || print "can\'t open taxa\n";
my @data_taxa = <TSP>;
close TSP;

# read csv separated taxa-subspecies.csv from ITIS
open (TSUB, "<$taxa_sub") || print "can\'t open taxa subspecies\n";
my @data_taxasub = <TSUB>;
close TSUB;

# parse taxa data for taxa hiearchy of species
for $_(@data_taxa){
    my $line = $_;
    chomp $line;
    my @vals = split(',', $line);
    $pars{$vals[0]} = 0;
    $tax{$vals[0]} = 0;
    if($vals[2] =~ m/[0-9]+/){
        $pars{$vals[0]} = $vals[2];
        $tax{$vals[0]} = $vals[1]."-".$vals[3];
    }
}

# parse taxa data for taxa hiearchy of subspecies
for $_(@data_taxasub){
    my $line = $_;
    chomp $line;
    my @vals = split(',', $line);
    $pars_sub{$vals[0]} = 0;
    $tax_sub{$vals[0]} = 0;
    if($vals[2] =~ m/[0-9]+/){
        $pars_sub{$vals[0]} = $vals[2];
        $tax_sub{$vals[0]} = $vals[1]."-".$vals[3];
    }
}

# parse species data for parental tsn
# crawl hierarchy 
# create temporary file with "|" delimited column of hierarchy
for $_(@data_species){
    my $line = $_;
    chomp $line;
    my $tsn = 0;
    my @df = split('\t', $line);
    my $tsnp = $df[17];
    my $valid = $df[10];
    my $tsn = $df[0];
    my $rank_id = $df[21];
    my $species = $df[25];
    my $t = $species."-220";
    while($rank_id != '10' && $tsn != '' && ($valid eq 'accepted' or $valid eq 'valid')){
        print "$tsn,$tsnp ==>";
        print "$tax{$tsn},$tax{$tsnp}\n";
        $t .= "|".$tax{$tsn}."|".$tax{$tsnp};
        $tsn = $pars{$tsnp};
        $tsnp = $pars{$tsn};
    }
    $line .= "\t".$t;
    push(@d,$line);
}

# parse subspecies data for parental tsn
# crawl hierarchy 
# create temporary file with "|" delimited column of hierarchy
for $_(@data_subspecies){
    my $line = $_;
    chomp $line;
    my $tsn = 0;
    my @df = split('\t', $line);
    my $tsnp = $df[17];
    my $valid = $df[10];
    my $tsn = $df[0];
    my $rank_id = $df[21];
    my $species = $df[25];
    my $t = $species."-230";
    while($rank_id != '10' && $tsn != '' && ($valid eq 'accepted' or $valid eq 'valid')){
        print "$tsn,$tsnp ==>";
        print "$tax_sub{$tsn},$tax_sub{$tsnp}\n";
        $t .= "|".$tax_sub{$tsn}."|".$tax_sub{$tsnp};
        $tsn = $pars_sub{$tsnp};
        $tsnp = $pars_sub{$tsn};
    }
    $line .= "\t".$t;
    push(@d,$line);
}

# write temporary file with the hierarchy for each species line
open (OUT,">>$outfile_temp") || print "can\'t open $outfile_temp\n";
for $_(@d){
    print OUT $_."\n";
}
close OUT;

# using temporary file from above, crawl hierarchy hash until kingdom reached
# capture hierarchy for each species as columns and print to file
open (IN,"<$outfile_temp") || print "can\'t open $outfile_temp\n";
open (OUT2,">>$outfile") || print "can\'t open $outfile\n";
print OUT2 "tsn\tunit_ind1\tunit_name1\tunit_ind2\tunit_name2\tunit_ind3\tunit_name3\tunit_ind4\tunit_name4\tunnamed_taxon_ind\tname_usage\tunaccept_reason\tcredibility_rtng\tcompleteness_rtng\tcurrency_rating\tphylo_sort_seq\tinitial_time_stamp\tparent_tsn\ttaxon_author_id\thybrid_author_id\tkingdom_id\trank_id\tupdate_date\tuncertain_prnt_ind\tn_usage\tcomplete_name\tkingdom\tsubkingdom\tphylum\tsubphylum\tsuperclass\tclass\tsubclass\tinfraclass\tsuperorder\torder\tsuborder\tinfraorder\tsection\tsubsection\tsuperfamily\tfamily\tsubfamily\ttribe\tsubtribe\n";
for $_(<IN>){
    my ($a1,$kingdom,$subking,$phylum,$subphylum,$superclass,$class,$subclass,$infraclass,$superorder,$order,$suborder,$infraorder,$section,$subsection,$superfamily,$family,$subfamily,$tribe,$subtribe,$genus,$species,$subspecies) = "";
    my $line = $_;
    chomp $line;

    my @l = split("\t",$line);
    my $tx1 = pop(@l);
    for $_(@l){
        $a1 .= $_."\t";
    }
    my @info = split(/\|/,$tx1);
    for $_(@info){
        my $val = $_;
        chomp $val;
        if($val =~ m/(.*)-10$/){
            $kingdom = $1;
        }
        elsif($val =~ m/(.*)-20$/){
            $subking = $1;
        }
        elsif($val =~ m/(.*)-30$/){
            $phylum = $1;
        }
        elsif($val =~ m/(.*)-40$/){
            $subphylum = $1;
        }
        elsif($val =~ m/(.*)-50$/){
            $superclass = $1;
        }
        elsif($val =~ m/(.*)-60$/){
            $class = $1;
        }
        elsif($val =~ m/(.*)-70$/){
            $subclass = $1;
        }
        elsif($val =~ m/(.*)-80$/){
            $infraclass = $1;
        }
        elsif($val =~ m/(.*)-90$/){
            $superorder = $1;
        }
        elsif($val =~ m/(.*)-100$/){
            $order = $1;
        }
        elsif($val =~ m/(.*)-110$/){
            $suborder = $1;
        }
        elsif($val =~ m/(.*)-120$/){
            $infraorder = $1;
        }
        elsif($val =~ m/(.*)-124$/){
            $section = $1;
        }
        elsif($val =~ m/(.*)-126$/){
            $subsection = $1;
        }
        elsif($val =~ m/(.*)-130$/){
            $superfamily = $1;
        }
        elsif($val =~ m/(.*)-140$/){
            $family = $1;
        }
        elsif($val =~ m/(.*)-150$/){
            $subfamily = $1;
        }
        elsif($val =~ m/(.*)-160$/){
            $tribe = $1;
        }
        elsif($val =~ m/(.*)-170$/){
            $subtribe = $1;
        }
    }
    
    my $i;
    
    unless($a1 =~ m/tsn/){
        print OUT2 $a1."$kingdom\t$subking\t$phylum\t$subphylum\t$superclass\t$class\t$subclass\t$infraclass\t$superorder\t$order\t$suborder\t$infraorder\t$section\t$subsection\t$superfamily\t$family\t$subfamily\t$tribe\t$subtribe\n";
    }
}
close IN;
close OUT;
