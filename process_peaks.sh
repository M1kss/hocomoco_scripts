#!/bin/bash

out_path=$1
genome=$2
peaks_path="/home/boytsov/hocomoco-peaks/"$3

if [ ! -d "$peaks_path" ]
then
  echo "Peaks have not been downloaded $peaks_path"
  exit 0
fi
peaks_name=$(basename $peaks_path)
for peak_dir in $peaks_path/*
do
  peak_type=$(basename $peak_dir)
  for score_type in score pvalue
  do
    if [ $peak_type == "cpics" ] && [ $score_type == 'pvalue' ]
    then
      continue
    fi
    echo "Now doing $peaks_path/$peak_type/$peaks_name"
    if ! python3 format_peaks.py $peaks_path/$peak_type/$peaks_name.interval $peak_type $score_type $out_path/raw/${peaks_name}.${peak_type}.${score_type}.bed 1>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.format.log 2>&1
    then
      echo "Format peaks failed: $peaks_path/$peak_type/$peaks_name.interval"
      continue
    fi
    if ! bedtools sort -i $out_path/raw/${peaks_name}.${peak_type}.${score_type}.bed 1> $out_path/sorted/${peaks_name}.${peak_type}.${score_type}.sorted.bed 2>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.sort.log
    then
      echo "Bed tools failed: $out_path/raw/${peaks_name}.${peak_type}.${score_type}.bed"
      continue
    fi
    if ! python3 cut_fasta.py $genome $out_path/sorted/${peaks_name}.${peak_type}.${score_type}.sorted.bed $out_path/fasta/${peaks_name}.${peak_type}.${score_type}.mfa 1>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.cut.log 2>&1
    then
      echo "Cut fasta failed: $out_path/sorted/${peaks_name}.${peak_type}.${score_type}.sorted.bed"
      continue
    fi
  done
done
