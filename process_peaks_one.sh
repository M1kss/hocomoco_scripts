#!/bin/bash
#PBS -l walltime=48:00:00,nodes=1:ppn=2

HOCOLINE=$(awk "{if(NR==$PBS_ARRAYID) print $0}" hoco-master.tsv)
IFS=','
read -ra ARRAY <<< "$HOCOLINE"

#specie=${ARRAY[0]}
#tf=${ARRAY[1]}
peaks_name=${ARRAY[2]}
peak_type=${ARRAY[3]}
score_type=${ARRAY[4]}
motif_type=${ARRAY[5]}
max_len=${ARRAY[6]}
min_len=${ARRAY[7]}

out_path=''

echo $out_path/fasta/${peaks_name}.${peak_type}.${score_type}

#if [ "$motif_type" == 'single' ]; then
#  java -Xmx4G -cp ~/chipmunk.jar ru.autosome.ChIPHorde ${min_len}:${max_len},${min_len}:${max_len} f c 1.0 m:$out_path/fasta/${peaks_name}.${peak_type}.${score_type}.mfa 100 10 1 2 random auto single 1>$out_path/results/${peaks_name}.${peak_type}.${score_type}.single.out 2>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.single.log
#fi
#
#if [ "$motif_type" == 'flat' ]; then
#  java -Xmx4G -cp ~/chipmunk.jar ru.autosome.ChIPHorde ${max_len}:${min_len},${max_len}:${min_len} f c 1.0 m:$out_path/fasta/${peaks_name}.${peak_type}.${score_type}.mfa 100 10 1 2 random auto 1>$out_path/results/${peaks_name}.${peak_type}.${score_type}.flat.out 2>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.flat.log
#fi
