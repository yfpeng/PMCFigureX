#!/bin/bash

export PYTHONPATH=.

disease='Adenoid cystic carcinoma'
#source_dir=$HOME'/Subjects/PMCFigureX'
#venv_dir=$HOME'/Subjects/venvs/pengyifan-wcm'
data_dir=$HOME'/Data/derm'

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
subfigure_file=$disease_dir/$prefix.subfigures.csv

subfigure_dir=$disease_dir
[ -d "$subfigure_dir" ] || mkdir "$subfigure_dir"
[ -d "$subfigure_dir/images" ] || mkdir "$subfigure_dir/images"
[ -d "$subfigure_dir/labels" ] || mkdir "$subfigure_dir/labels"


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
    'step4' )
      echo "step4: prepare subfigures"
      python figurex/prepare_subfigures.py -i "$figure_file" -f "$bioc_dir" -o "$subfigure_dir"
      ;;
    'step5' )
      echo "step5: Extract subfigures"
      python figurex/get_subfigures.py -i "$figure_file" -o "$subfigure_file" -f "$bioc_dir"
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done
