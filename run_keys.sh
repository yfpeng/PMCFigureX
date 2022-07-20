#!/bin/bash

export PYTHONPATH=.

disease='edema'
#source_dir=$HOME'/Subjects/PMCFigureX'
#venv_dir=$HOME'/Subjects/venvs/pengyifan-wcm'
data_dir=$HOME'/Data/PMCFigureX'

#cd "$source_dir" || exit
#source "$venv_dir"/bin/activate

# create dir
bioc_dir=$data_dir/bioc
[ -d "$bioc_dir" ] || mkdir "$bioc_dir"

prefix=$disease
query="(pubmed pmc open access[filter]) AND (${disease}[Title/Abstract])"
oa_file=$data_dir/"oa_file_list.csv"

# data
disease_dir=$data_dir/$disease
[ -d "$disease_dir" ] || mkdir "$disease_dir"

pmc_export_file=$disease_dir/$prefix.export2.csv
figure_file=$disease_dir/$prefix.figures.csv


while [ "$1" != "" ]; do
  case "$1" in
    'step1' )
      echo "step1: Query PubMed" $query
      python figurex/query_pubmed.py -q "$query" -o "$pmc_export_file"
      ;;
    'step2' )
      echo "step2: Download tar gz"
      step2output=$disease_dir/$prefix.export-step2.csv
      python figurex/get_tar_gz_thread.py -i "$pmc_export_file" -o "$step2output" -a "$oa_file" -f "$bioc_dir"
      ;;
    'step3' )
      echo "step3: Extract figures"
      python figurex/extract_figures_thread.py -i "$pmc_export_file" -o "$figure_file" -f "$bioc_dir"
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done
