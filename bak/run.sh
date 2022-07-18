#!/bin/bash

export PYTHONPATH=.

api_key="8def8567d05fa247c9a721214c6bbd107408 "
email='pengyifan.mail@gmail.com'

#api_key="0530ab6a813bee8d2d5de7929db6e6796809 "
#email='yifan.peng@nih.gov'

source_dir='/home/yip4002/Subjects/PMCFigureX/'
venv_dir='/home/yip4002/Subjects/venvs/PMCFigureX'
cd $source_dir || exit
source "$venv_dir/bin/activate"

top_dir='/home/yip4002/data/covid'
figure_separation_model=$top_dir/../models/figure-separation-model-submitted-544.pb
cxr_ct_model=$top_dir/../models/normal_cxr_ct_label_densenet121_bs32_h214_w214_2020-04-13T0026_best_model.h5

prefix='08082020.litcovid'
data_dir=$top_dir/'08082020'

history_prefix='05092020.litcovid'
history_data_dir=$top_dir/'05092020'

# data
litcovid_file=$data_dir/$prefix.export.tsv
pmc_file=$data_dir/$prefix.pmc.csv
total_figure_file=$data_dir/$prefix.total_figures.csv
local_figure_file=$data_dir/$prefix.local_figures.csv
subfigure_file=$data_dir/$prefix.local_subfigures.csv
prediction_file=$data_dir/$prefix.local_subfigures_pred.csv
gold_file=$data_dir/$prefix.local_subfigures_gold.csv
released_file=$data_dir/${prefix}.released.csv
xml_file=$data_dir/$prefix.released.json

check_dir=$data_dir/$prefix.subfigures_cxr_ct_pred

# history data
history_pmc_file=$history_data_dir/$history_prefix.pmc.csv
history_gold_file=$history_data_dir/$history_prefix.local_subfigures_gold.csv

bioc_dir=$data_dir/../bioc
[ -d $bioc_dir ] || mkdir $bioc_dir

medline_dir=$data_dir/../medline
[ -d $medline_dir ] || mkdir $medline_dir

figure_dir=$data_dir/../figures
[ -d $figure_dir ] || mkdir $figure_dir

subfigure_dir=$data_dir/../subfigures_json
[ -d $subfigure_dir ] || mkdir subfigure_dir

while [ "$1" != "" ]; do
  case "$1" in
    'step1' )
      echo "step1: Get PMC ID from PubMed"
      if [[ -f $history_pmc_file ]]; then
        python figurex/get_pmc_from_pubmed.py -i $litcovid_file -o $pmc_file -l $history_pmc_file
      else
        python figurex/get_pmc_from_pubmed.py -i $litcovid_file -o $pmc_file
      fi
      ;;
    'step2' )
      echo "step2: Get BioC files"
      python figurex/get_bioc.py -i $pmc_file -o $bioc_dir
      ;;
    'step3' )
      echo "step3: Get MedLine"
      python figurex/get_medline.py -i $pmc_file -o $medline_dir --email $email --api-key $api_key
      ;;
    'step4' )
      echo "step4: Get figures"
      python figurex/get_figure_url.py -i $pmc_file -o $total_figure_file -b $bioc_dir
      ;;
    'step5' )
      echo "step5: Download local figures"
      python figurex/get_figures.py -i $total_figure_file -o $local_figure_file -f $figure_dir
      ;;
    'step6' )
      echo "step6: Split figures"
      python figurex/split_figures.py \
        -i $local_figure_file \
        -o $subfigure_file \
        -f $figure_dir \
        -s $subfigure_dir \
        -m $figure_separation_model
      ;;
    'step7' )
      echo "step7: Classify CT CXR"
      python figurex/classify_cxr_ct.py \
        -i $subfigure_file \
        -o $prediction_file \
        -f $figure_dir \
        -l $history_gold_file \
        -m $cxr_ct_model
      ;;
    'step8' )
      echo "step8: Collect CT CXR to check"
      python figurex/collect_predictions_to_check.py \
        -i $prediction_file \
        -o $check_dir \
        -f $figure_dir \
        -l $history_gold_file
      ;;
    'step9' )
      echo "step9: Collect gold standard CT CXR"
      python figurex/collect_gold_standard.py \
        -i $prediction_file \
        -o $gold_file \
        -f $check_dir \
        -l $history_gold_file
      ;;
    'step10' )
      echo "step10: Create released gold standard CT CXR"
      python figurex/gold_standard_to_publish.py \
        -i $gold_file \
        -o $released_file
      ;;
    'step11' )
      echo "step11: Extract CT CXR text"
      python figurex/get_figure_text.py \
        -i $released_file \
        -o $xml_file \
        -b $bioc_dir
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done
