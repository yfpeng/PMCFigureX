#!/bin/bash

export PYTHONPATH=.

source_dir=$HOME'/Subjects/PMCFigureX/'
venv_dir=$HOME'/Subjects/venvs/PMCFigureX'
cd $source_dir || exit
source "$venv_dir/bin/activate"

top_dir=$HOME/'Data/PMCFigureX'
figure_separation_model=$top_dir/models/figure-separation-model-submitted-544.pb
cxr_ct_model=$top_dir/models/normal_cxr_ct_label_densenet121_bs32_h214_w214_2020-04-13T0026_best_model.h5

# create dir
bioc_dir=$top_dir/bioc
[ -d $bioc_dir ] || mkdir $bioc_dir

#figure_dir=$top_dir/figures
#[ -d $figure_dir ] || mkdir $figure_dir

database_file=$top_dir/covid.db

prefix='pneumoperitoneum'
# data
data_dir=$top_dir/$prefix
litcovid_file=$data_dir/$prefix.export.tsv

subfigure_file=$data_dir/$prefix.subfigures.csv
prediction_subfigure_file=$data_dir/$prefix.subfigures_pred.csv

figure_file=$data_dir/$prefix.figures.csv
prediction_figure_file=$data_dir/$prefix.figures_pred.csv

text_file=$data_dir/$prefix.figure_text.json


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
    'step6' )
      echo "step6: Split figures"
      python figurex_db/split_figures.py -d $database_file -f $bioc_dir -m $figure_separation_model
      ;;
    'step7' )
      echo "step7: Get local figures/subfigures"
      python figurex_db/get_subfigures.py -d $database_file -f $bioc_dir --ds $subfigure_file --df $figure_file
      ;;
    'step8' )
      echo "step8: Classify CT CXR normal subfigures"
      src_tmp=$subfigure_file
      dst_tmp=$prediction_subfigure_file
      hit_tmp=$history_prediction_subfigure_file

      if [[ -v $hit_tmp ]] && [[ -f $hit_tmp ]]; then
        python figurex_db/classify_figures.py -f $bioc_dir -m $cxr_ct_model \
          -s $src_tmp -o $dst_tmp --history $hit_tmp
      else
        python figurex_db/classify_figures.py -f $bioc_dir -m $cxr_ct_model \
          -s $src_tmp -o $dst_tmp
      fi

      echo "step8: Classify CT CXR normal figures"
      src_tmp=$figure_file
      dst_tmp=$prediction_figure_file
      hit_tmp=$history_prediction_figure_file

      if [[ -v $hit_tmp ]] && [[ -f $hit_tmp ]]; then
        python figurex_db/classify_figures.py -f $bioc_dir -m $cxr_ct_model \
          -s $src_tmp -o $dst_tmp --history $hit_tmp
      else
        python figurex_db/classify_figures.py -f $bioc_dir -m $cxr_ct_model \
          -s $src_tmp -o $dst_tmp
      fi
      ;;
    'step9' )
      echo "step9: Get text"
      python figurex_db/get_figure_text.py -f $bioc_dir -d $text_file \
        --ds $prediction_subfigure_file --df $prediction_figure_file
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done
