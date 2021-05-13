# Get started

## Prepare virtual environment

```bash
$ cd path/to/PMCFigureX
$ git clone https://github.com/yfpeng/PMCFigureX.git
$ cd path/to/PMCFigureX
$ virtualenv -p python3 /path/to/venv
$ source /path/to/venv
$ pip -r requirements
```

## Download pre-trained models

1. Download pre-trained model for figure separation at https://github.com/apple2373/figure-separator
2. Donwload the CXR/CT classifier at https://github.com/ncbi-nlp/COVID-19-CT-CXR/releases/tag/v20200610

## Prepare source file

1. Go to https://pubmed.ncbi.nlm.nih.gov/
2. Search disease. For example `Atelectasis [all_field]`. Note: PubMed will automatically find synonyms of atelectasis, 
   e.g., `"pulmonary atelectasis"[MeSH Terms] OR ("pulmonary"[All Fields] AND "atelectasis"[All Fields]) OR "pulmonary 
   atelectasis"[All Fields] OR "atelectasis"[All Fields]`
3. On the left, click "Free full text"
4. Click "Save" and choose the "CSV" format: `/path/to/Atelectasis.export.csv`

## Convert PubMed export file

```bash
$ python figurex_db/convert_pubmed_search_output.py \
    -s /path/to/Atelectasi.export.csv \
    -d /path/to/Atelectasi.export.tsv
```

## Run the script

Change the paths in `run_keys_db.sh`

```text
disease='Atelectasis'
source_dir=$HOME'/path/to/PMCFigureX'
venv_dir=$HOME'/path/to/venv'
top_dir=$HOME'/path/to/Atelectasi.export.tsv'
```

```bash
$ bash run_keys_db.sh step1 step2 step3 step4 step5 step6 step7 step8
```

The output is at `/path/to/Atelectasis.figure_text.json`

# Acknowledgments

This work was supported by NLM under award number 4R00LM013001 and the Intramural Research Programs of the 
National Institutes of Health. It was als supported by the Google COVID-19 Research Grant.
