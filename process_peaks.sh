
peaks_path=$3
out_path=$1
genome=$2
peaks_name=$(basename $peaks_path)

if ! [ -d $peaks_path ];
then
  echo "Peaks have not been downloaded $peaks_path"
  exit 0
fi

for peak_dir in $peaks_path/*
do
  peak_type=$(basename $peak_dir)
  for score_type in score pvalue
  do
    if [ $peak_type == "cpics" ] && [ $score_type == 'pvalue' ]
    then
      continue
    fi
    if ! python3 format_peaks.py $peaks_path/$peak_type/$peaks_name.interval $peak_type $score_type $out_path/raw/${peaks_name}.${peak_type}.${score_type}.bed 1>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.format.log 2>&1
    then
      continue
    fi
    bedtools sort -i $out_path/raw/${peaks_name}.${peak_type}.${score_type}.bed 1> $out_path/sorted/${peaks_name}.${peak_type}.${score_type}.sorted.bed 2>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.sort.log
    if ! python3 cut_fasta.py $genome $out_path/sorted/${peaks_name}.${peak_type}.${score_type}.sorted.bed $out_path/fasta/${peaks_name}.${peak_type}.${score_type}.mfa 1>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.cut.log 2>&1
    then
      continue
    fi

    java -Xmx4G -cp ~/chipmunk.jar ru.autosome.di.ChIPHorde 7:28,7:28 f c 1.0 m:$out_path/fasta/${peaks_name}.${peak_type}.${score_type}.mfa 400 40 1 2 random auto single 1>$out_path/results/${peaks_name}.${peak_type}.${score_type}.single.out 2>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.single.log
    java -Xmx4G -cp ~/chipmunk.jar ru.autosome.di.ChIPHorde 28:7,28:7 f c 1.0 m:$out_path/fasta/${peaks_name}.${peak_type}.${score_type}.mfa 400 40 1 2 random auto 1>$out_path/results/${peaks_name}.${peak_type}.${score_type}.flat.out 2>$out_path/logs/${peaks_name}.${peak_type}.${score_type}.flat.log
  done
done
