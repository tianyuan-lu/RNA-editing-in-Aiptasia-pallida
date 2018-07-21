# RNA editing in Aiptasia pallida
---
This is the detailed workflow for calling RNA editing sites in Aiptasia pallida and looking into endosymbiotic effects in a transcriptomic level.

This workflow requires assembled and annotated reference genome and raw reads. In our case, we had whole-genome RNA sequencing data of both aposymbiotic and symbiotic Aiptasia.

### Pre-mapping treatment
---
1. trimming with trimgalore:

       trim_galore --phred33 --length 25 --max_n 2 --trim-n --paired <file_R1.fastq> <file_R2.fastq>
    
This step retains paired-end reads longer than 25 bps, with maximum 2 "N"s and without flanking Ns. The trimming applies default low-quality threshold of 20. To adjust: -q <num>
  
2. removing first 6 bases:

       awk '{if (NR %2 ==1) print; if (NR %2 ==0) print substr($0, 7)}' <trimmed.file.fastq>
    
This step avoids mapping errors caused by random-hexamer primers (F Zhang, 2017).

### Mapping
---
3. mapping with bwa

       bwa index <reference.genome.fa>
    
       bwa mem <reference.genome.fa> <R1.trimmed.rm6p.fastq> <R2.trimmed.rm6p.fastq>
    
If alignment yields sam files, for further analysis, they should be converted to bam files.

    samtools view -bS <aln.sam> > <aln.bam>
    
All bam files should be sorted.

    samtools sort <aln.bam> > <sorted.aln.bam>

### Calling RNA editing sites
---
SPRINT may support calling RNA editing sites directly from raw reads (which should also go through Pre-mapping treatment), but it was not compatible with our system.

So alternatively, we started using SPRINT only after obtaining aligned bam files.

4. calling RNA editing sites with SPRINT

       sprint_from_bam <sorted.aln.bam> <reference.genome.fa> <output> <location of samtools>
    
Results of SPRINT annotate types and strands of transcriptomic variants.

5. converting annotation

       python3 convert.py <RES> > <converted.RES.tsv>
  
This step unifies variants based on the "+" strand of the reference. To check distribution of variant types:

    awk '{col[$3,$4]++}END{for(i in col) print i, col[i]}' <converted.RES.tsv> | sort -k2 -n -r
    
Hopefully A>I conversion dominates the distribution.

6. tabulating

       python3 tabulate_tsvs.py <all.converted.RES.tsvs> -k 0 1 2 3 -c 4 5 -v > tabulated.RES.tsv
    
This step tabulates all potential RNA editing sites who occur at least once in all replicates.

tabulate_tsvs.py can be found at https://github.com/lyijin/working_with_dna_methylation

7. filtering for bona fide RNA editing sites

For a potential RNA editing site to be considered as bona fide, it has to meet these criteria:

$1. has a mean total coverage in all replicates >= 10;

$2. has a median total coverage in all replicates >= 5;

(optional) $3. be present in all replicates.

    python3 bonafideRNA.py tabulated.RES.tsv > bonafide.tsv
    
Till this step, we got bona fide RNA editing sites in aposymbiotic and symbiotic Aiptasia, respectively.

Then we did comparison between these two to find out: RES only in aposymbiotic, RES only in symbiotic, and differentially edited sites.

8. looking for differentially edited sites

       python3 ttest.py A.bonafide.tsv S.bonafide.tsv > compare_A_to_S.tsv
    
This step generates a table containing common RES in aposymbiotic and symbiotic Aiptasia and compares the levels of RNA editing. 

T test compares mean RNA editing levels of all replicates in aposymbiotic and symbiotic Aiptasia, assuming non-equal variances.

    awk '{print $NF}' compare_A_to_S.tsv > p.values.txt
    
    python3 correct_p_values.py p.values.txt > corrected.p.values.txt
    
    paste compare_A_to_S.tsv corrected.p.values.txt > corrected_comparison_A_to_S.tsv
    
This step corrects p values using a pre-written script (https://github.com/lyijin/common). Default method is Benjamini-Hochberg.

9. looking for unique RES

       python3 onlyinfirst.py A.bonafide.tsv S.bonafide.tsv > onlyinA.tsv
    
       python3 onlyinfirst.py S.bonafide.tsv A.bonafide.tsv > onlyinS.tsv
    
Here comes an issue: if we require omnipresence of potential RES in all replicates in step 7.$3,

we may find some so-called unique RESs also appear in the other bonafide.tsv.

e.g. scaffold X position Y is a detected RES in aposymbiotic Aiptasia which can be proved by all aposymbiotic replicates.

However, there are 5 in 6 replicates of symbiotic Aiptasia samples also show this specific RES. Since it does not meet the criterion of omnipresence, it has been filtered out.

Is it reasonable?

So we suggest disabling 7.$3 in filtering and following next steps.

### Contrasting, validating and analysing
---
10. generating coverage tables

After silencing 7.$3, we found blanks in bonafide.tsv (as in tabulated.RES.tsv).

These blanks represent either no coverage in raw reads, or no variant in any read.

To determine whether they should be annotated as NA or 0 (it matters because only the latter will be taken into t test), we generated coverage tables from aligned bam files.   

    samtools mpileup -f reference.genome.fa sorted.aln.bam > pileup.tsv
    
    python3 tabulate_tsvs.py <all.pileup.tsvs> -k 0 1 2 -c 3 -v > coverage.tsv 
    
We did mpileup on these aligned bam files separately and tabulated coverage tables for aposymbiotic and symbiotic samples.

    python3 fillinblank.py coverageA/S.tsv A/S.bonafide.tsv > full.A/S/bonafide.tsv
    
In the "full" tsvs, "-1/10000" dictates no coverage in the specific position in the specific replicate, while "0/10000" dictates no detected RES despite coverage.

Then, we went back and carried out step 8, this time the comparison should be more comprehensive. Finally we carried out step 9 and generated onlyinA/S.tsvs.

11. validating black-and-whites

For RES only present in one condition, we hope they are:

$1. covered in reads from the other condition

$2. non-variated in the other condition

However, previous steps only guarantee $2.

To validate positions in onlyinA/S.tsvs, we again need to check their coverage in the coverageS/A.tsv, respectively.

    python3 findcoverage.py coverageS/A.tsv onlyinA/S.tsv > check_unique_coverage.A/S.tsv
    
As long as a row appears no coverage in any replicate, the uniqueness of corresponding position is unconvincing and this position should be discarded.

From this point on, we entered the stage of enrichment.

12. Annotating

We used SnpEff to annotate important sites. We had assembled Aiptasia genome and its gff3 annotation. In our case, we mainly looked into:

diffrentially edited sites, uniquely edited sites, and biologically meaningful edited sites (e.g. symnonymous/non-symnonymous variants)

Installation instructions can be found at http://snpeff.sourceforge.net/SnpEff_manual.html#intro

We built our own database (which is required for non-model organisms) following http://snpeff.sourceforge.net/SnpEff_manual.html#databases

In some cases conversion of gff3 to gtf is mandatory.

    gffread genome.scaffold.gff3 -T -o genome.scaffold.gtf
    
Before annotating, we reconstructed our files to vcf files.

This process requires extraction of interested positions and related information from files generated previously. Command line should be suffice.

    java -jar snpEff.jar -v -no-upstream -no-downstream <name.of.manually.created.database> <results.vcf> > annotated.vcf
    
To extract only gene IDs and genomic context, use

    python3 extract.py annotated.vcf > anno.results.tsv
    
13. Enrichment

Online searching engine can complete individual annotations based on gene IDs: http://lithium.kaust.edu.sa:9999/

Self-written scripts can complete enrichment of lists of genes (by YJ Liew).

Researchers familiar with cellular/functional/structural biology of Aiptasia should be able to interpret results of the enrichment.

14. Designing primers

After having pinpointed interested genes, we did PCR verification on extracted RNA (reverse-transcribed to cDNA).

    design_generic_primers.py <reference.genome.fa> <desired.amplicons.tsv>
    
Required format of the tsv file is defined at https://github.com/lyijin/common/blob/master/design_generic_primers.py

Before deciding on "starting coordinates" and "ending cooridinates", we checked whether corresponding positions are transcribable, i.e. both starting and ending coordinates of a targeted RES in exon should also fall in exon regions.
In our case, the lengths of amplicons vary between 180 to 200 bps.
