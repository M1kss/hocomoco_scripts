#!/bin/bash

out_path=$1
genome=$2
njobs=$3

for peak_full in $out_path/sorted/*
do
  echo $peak_full
  IFS='.'
  read -ra ADDR <<< "$peak_full"
  peak_name=${ADDR[0]}
  peak_type=${ADDR[1]}
  score_type=${ADDR[2]}
  if [ $peak_type == "cpics" ] && [ $score_type == 'pvalue' ]
  then
    continue
  fi
  echo "Now doing $peaks_path/$peak_type/$peak_name, $score_type"
#  if ! bedtools getfasta -fi $genome -bed $peak_name -name 2>$out_path/logs/${peak_name}.${peak_type}.${score_type}.cut.log | awk -F':' '{print $1}' 1>$out_path/fasta/${peak_name}.${peak_type}.${score_type}.mfa 2>>$out_path/logs/${peak_name}.${peak_type}.${score_type}.cut.log
#  then
#    echo "Cut fasta failed: $out_path/sorted/${peak_name}.${peak_type}.${score_type}.sorted.bed"
#    continue
#  fi
done

