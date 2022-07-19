#!/bin/bash

# SET PYTHONPATH=.
export PYTHONPATH=.

disease='edema'
source_dir=$HOME'/Subjects/PMCFigureX'
venv_dir=$HOME'/Subjects/venvs/pengyifan-wcm'
top_dir=$HOME'/Data/PMCFigureX'


cd $source_dir || exit
source $venv_dir'/bin/activate'

figure_separation_model=$top_dir/models/figure-sepration-model-submitted-544.pb
cxr_ct_model=$top_dir/models/normal_cxr_ct_label_densenet121_bs32_h214_w214_2020-04-13T0026_best_model.h5

# create dir
bioc_dir=$top_dir/bioc
[ -d "$bioc_dir" ] || mkdir "$bioc_dir"

database_file=$top_dir/database.db

prefix=$disease
query="(pubmed pmc open access[filter]) AND (${disease}[Title/Abstract])"
oa_file=$top_dir/"oa_file_list.csv"

# data
data_dir=$top_dir/$disease
pmc_export_file=$data_dir/$prefix.export.csv
figure_file=$data_dir/$prefix.figures.csv

subfigure_file=$data_dir/$prefix.subfigures.csv
prediction_subfigure_file=$data_dir/$prefix.subfigures_pred.csv

figure_file=$data_dir/$prefix.figures.csv
prediction_figure_file=$data_dir/$prefix.figures_pred.csv

text_file=$data_dir/$prefix.figure_text.json
docx_file=$data_dir/$prefix.figure_text.docx
html_file=$data_dir/$prefix.figure_text.html
bioc_file=$data_dir/$prefix.figure_text.xml
neg_file=$data_dir/$prefix.figure_text_${prefix}_neg.xml

history_prediction_subfigure_file=None
history_prediction_figure_file=None

while [ "$1" != "" ]; do
  case "$1" in
    'step1' )
      echo "step1: Query PubMed"
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
    'step6' )
      echo "step6: Split figures"
      python figurex_db/split_figures.py -d "$database_file" -f "$bioc_dir" -m "$figure_separation_model"
      ;;
    'step7' )
      echo "step7: Get local figures/subfigures"
      python figurex_db/get_subfigures.py -d "$database_file" -f "$bioc_dir" --ds "$subfigure_file" --df "$figure_file"
      ;;
    'step8' )
      echo "step8: Classify CT CXR normal subfigures"
      src_tmp=$subfigure_file
      dst_tmp=$prediction_subfigure_file
      hit_tmp=$history_prediction_subfigure_file

      if [ -z "$hit_tmp" ] && [ -f "$hit_tmp" ]; then
        python figurex_db/classify_figures.py -f "$bioc_dir" -m "$cxr_ct_model" \
          -s "$src_tmp" -o "$dst_tmp" --history $hit_tmp
      else
        python figurex_db/classify_figures.py -f "$bioc_dir" -m "$cxr_ct_model" \
          -s "$src_tmp" -o "$dst_tmp"
      fi

      echo "step8: Classify CT CXR normal figures"
      src_tmp=$figure_file
      dst_tmp=$prediction_figure_file
      hit_tmp=$history_prediction_figure_file

      if [ -z "$hit_tmp" ] && [ -f "$hit_tmp" ]; then
        python figurex_db/classify_figures.py -f $bioc_dir -m $cxr_ct_model \
          -s "$src_tmp" -o "$dst_tmp" --history $hit_tmp
      else
        python figurex_db/classify_figures.py -f $bioc_dir -m $cxr_ct_model \
          -s "$src_tmp" -o "$dst_tmp"
      fi
      ;;
    'step9' )
      echo "step9: Get text"
      python figurex_db/get_figure_text.py -f "$bioc_dir" -d "$text_file" \
        --ds "$prediction_subfigure_file" --df "$prediction_figure_file"
      ;;
    'step10' )
      echo "step10: HTML for demonstration"
#      python figurex_db/convert_to_html.py -f "$bioc_dir" -s "$text_file" -d "$html_file" --disease "$disease"
      python figurex_db/convert_to_html_neg.py -f "$bioc_dir" -s "$text_file" -d "$html_file" --disease "$disease" \
        --neg "$neg_file"
      ;;
    'step11' )
      echo "step 11: Convert to docx"
      pandoc -s -f html -t docx "$html_file" -o "$docx_file"
      ;;
    'step12' )
      echo "step 12: BioC for ptake"
      python figurex_db/convert_to_bioc.py -s "$text_file" -d "$bioc_file"
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done
