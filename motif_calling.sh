njobs=$1
out_path=$2
genome=$3
peaks_list=$4

if ! [ -d $out_path ]
then
  mkdir $out_path
  for suffix in results logs raw sorted fasta
  do
    if ! [ -d $out_path/$suffix ]
    then
      mkdir $out_path/$suffix
    fi
  done
fi



parallel --jobs $njobs bash process_peaks.sh $out_path $genome :::: $peaks_list
