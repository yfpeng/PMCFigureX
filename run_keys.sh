#!/bin/bash

# SET PYTHONPATH=.
export PYTHONPATH=.

disease='pneumothorax'
source_dir=$HOME'/Subjects/PMCFigureX'
venv_dir=$HOME'/Subjects/venvs/pengyifan-wcm'
top_dir=$HOME'/Data/PMCFigureX'

cd "$source_dir" || exit
source "$venv_dir"/bin/activate

# create dir
bioc_dir=$top_dir/bioc
[ -d "$bioc_dir" ] || mkdir "$bioc_dir"

prefix=$disease
query="(pubmed pmc open access[filter]) AND (${disease}[Title/Abstract])"
oa_file=$top_dir/"oa_file_list.csv"

# data
data_dir=$top_dir/$disease
[ -d "$data_dir" ] || mkdir "$data_dir"

pmc_export_file=$data_dir/$prefix.export.csv
figure_file=$data_dir/$prefix.figures.csv


while [ "$1" != "" ]; do
  case "$1" in
    'step1' )
      echo "step1: Query PubMed" $query
      python figurex/query_pubmed.py -q "$query" -o "$pmc_export_file"
      ;;
    'step2' )
      echo "step2: Download BioC files"
      python figurex/get_bioc.py -i "$pmc_export_file" -b "$bioc_dir"
      ;;
    'step3' )
      echo "step3: Get figures"
      python figurex/get_figure_url.py -i "$pmc_export_file" -o "$figure_file" -b "$bioc_dir"
      ;;
    'step4' )
      echo "step4: Download tar gz"
      python figurex/get_tar_gz.py -i "$figure_file" -o "$oa_file" -f "$bioc_dir"
      ;;
    'step5' )
      echo "step5: Extract local figures"
      python figurex/get_figures.py -i "$figure_file" -f "$bioc_dir"
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done
