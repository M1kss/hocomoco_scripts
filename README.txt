Scripts order:
move_mouse_peaks.py
craft_master.py
motif_calling.sh <out_dir>
parallel --jobs <jobs> make_fasta_from_peaks.sh <out_dir> <genome> <peaks_path> :::: <file with only peaks>
parallel --jobs <jobs> process_fasta_by_line.sh <out_dir> :::: master_peaks.csv

