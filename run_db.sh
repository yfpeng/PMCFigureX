#!/bin/bash

export PYTHONPATH=.

source_dir='/home/yip4002/Subjects/PMCFigureX/'
venv_dir='/home/yip4002/Subjects/venvs/PMCFigureX'
cd $source_dir || exit
source "$venv_dir/bin/activate"

top_dir='/home/yip4002/data/covid'

# create dir
bioc_dir=$top_dir/bioc
[ -d $bioc_dir ] || mkdir $bioc_dir

#figure_dir=$top_dir/figures
#[ -d $figure_dir ] || mkdir $figure_dir

database_file=$top_dir/covid.db

prefix='08082020.litcovid'
# data
data_dir=$top_dir/'08082020'
litcovid_file=$data_dir/$prefix.export.tsv


while [ "$1" != "" ]; do
  case "$1" in
    'step1' )
      echo "step1: Create database"
      python figurex_db/create_db.py -d $database_file
      ;;
    'step2' )
      echo "step2: Get PMC ID from PubMed"
      python figurex_db/get_pmc_from_pubmed.py -l $litcovid_file -d $database_file
      ;;
    'step3' )
      echo "step3: Get BioC files"
      python figurex_db/get_bioc.py -d $database_file -b $bioc_dir
      ;;
    'step4' )
      echo "step4: Get figures"
      python figurex_db/get_figure_url.py -d $database_file -b $bioc_dir
      ;;
    'step5' )
      echo "step5: Download local figures"
      python figurex_db/get_figures.py -d $database_file -f $bioc_dir
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done
