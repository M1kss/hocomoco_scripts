#!/bin/bash

out_path=$1
genome=$2
peaks_path=$3
peak_name=$4

if [ ! -d "$peaks_path" ]
then
  echo "No peaks found $peaks_path"
  exit 0
fi
peaks_name=$(basename $peaks_path)
for peak_dir in $peaks_path/*
do
  peak_type=$(basename $peak_dir)
  if [ ! -f "$peaks_path/$peak_type/$peak_name.interval" ]
    then
      echo "Empty folder with peaks: $peaks_path/$peak_type/"
      continue
  fi
  for score_type in score pvalue
  do
    if [ $peak_type == "cpics" ] && [ $score_type == 'pvalue' ]
    then
      continue
    fi
    echo "Now doing $peaks_path/$peak_type/$peaks_name, $score_type"
    if ! python3 format_peaks.py $peaks_path/$peak_type/$peak_name.interval $peak_type $score_type $out_path/raw/${peak_name}.${peak_type}.${score_type}.bed 1>$out_path/logs/${peak_name}.${peak_type}.${score_type}.format.log 2>&1
    then
      echo "Format peaks failed: $peaks_path/$peak_type/$peak_name.interval"
      continue
    fi
    if ! bedtools sort -i $out_path/raw/${peak_name}.${peak_type}.${score_type}.bed 1> $out_path/sorted/${peak_name}.${peak_type}.${score_type}.sorted.bed 2>$out_path/logs/${peak_name}.${peak_type}.${score_type}.sort.log
    then
      echo "Bed tools failed: $out_path/raw/${peak_name}.${peak_type}.${score_type}.bed"
      continue
    fi
    if ! bedtools getfasta -fi $genome -bed $out_path/sorted/${peak_name}.${peak_type}.${score_type}.sorted.bed -name 2>$out_path/logs/${peak_name}.${peak_type}.${score_type}.cut.log | awk -F':' '{print $1}' 1>$out_path/fasta/${peak_name}.${peak_type}.${score_type}.mfa 2>>$out_path/logs/${peak_name}.${peak_type}.${score_type}.cut.log
    then
      echo "Cut fasta failed: $out_path/sorted/${peak_name}.${peak_type}.${score_type}.sorted.bed"
      continue
    fi
  done
done
