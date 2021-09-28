out_path=$1


if ! [ -d $out_path ]
then
  if ! [ -d $out_path ]
  then
    mkdir $out_path
  fi
  for suffix in results logs raw sorted fasta
  do
    if ! [ -d $out_path/$suffix ]
    then
      mkdir $out_path/$suffix
    fi
  done
fi


#bash make_fasta_from_peaks.sh $out_path $genome $peaks_path
#parallel --jobs $njobs bash process_fasta_by_line.sh $out_path :::: $peaks_list
