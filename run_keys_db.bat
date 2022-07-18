SET PYTHONPATH=.

SET disease=pneumoperitoneum
SET top_dir=%userprofile%\Data\PMCFigureX

SET figure_separation_model=%top_dir%\models\figure-sepration-model-submitted-544.pb
SET cxr_ct_model=%top_dir%\models\normal_cxr_ct_label_densenet121_bs32_h214_w214_2020-04-13T0026_best_model.h5

SET bioc_dir=%top_dir%\bioc
SET data_dir=%top_dir%\%disease%

SET database_file=%top_dir%\database.db
SET figure_file=%data_dir%\%disease%.figures.csv
SET subfigure_file=%data_dir%\%disease%.subfigures.csv

python figurex_db\create_db.py -d ~\Data\PMCFigureX\database.db
python figurex_db\get_pmc_from_pubmed.py -l ~\Data\PMCFigureX\pneumoperitoneum.export.tsv -d ~\Data\PMCFigureX\database.db
python figurex_db\get_bioc.py -d %database_file% -b %bioc_dir%
python figurex_db\get_figure_url.py -d %database_file% -b %bioc_dir%
python figurex_db\get_figures.py -d %database_file% -f %bioc_dir%
python figurex_db\split_figures.py -d %database_file% -f %bioc_dir% -m %figure_separation_model%
python figurex_db\get_subfigures.py -d %database_file% -f %bioc_dir% --ds %subfigure_file% --df %figure_file%

SET src_tmp=%subfigure_file%
SET dst_tmp=%prediction_subfigure_file%
SET hit_tmp=%history_prediction_subfigure_file%
if exist %hit_tmp% (
    python figurex_db\classify_figures.py -f %bioc_dir% -m %cxr_ct_model% -s %src_tmp% -o %dst_tmp% --history %hit_tmp%
) else (
    python figurex_db\classify_figures.py -f %bioc_dir% -m %cxr_ct_model% -s %src_tmp% -o %dst_tmp%
)

SET src_tmp=%figure_file%
SET dst_tmp=%prediction_figure_file%
SET hit_tmp=%history_prediction_figure_file%

if exist %hit_tmp% (
    python figurex_db\classify_figures.py -f %bioc_dir% -m %cxr_ct_model% -s %src_tmp% -o %dst_tmp% --history %hit_tmp%
) else (
    python figurex_db\classify_figures.py -f %bioc_dir% -m %cxr_ct_model% -s %src_tmp% -o %dst_tmp%
)