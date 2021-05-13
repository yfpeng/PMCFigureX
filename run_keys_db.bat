SET PYTHONPATH=.

SET disease=pneumoperitoneum
SET top_dir=%userprofile%\Data\PMCFigureX

SET figure_separation_model=%top_dir%\models\figure-sepration-model-submitted-544.pb

SET bioc_dir=%top_dir%\bioc
SET database_file=%top_dir%\database.db

python figurex_db\create_db.py -d ~\Data\PMCFigureX\database.db
python figurex_db\get_pmc_from_pubmed.py -l ~\Data\PMCFigureX\pneumoperitoneum.export.tsv -d ~\Data\PMCFigureX\database.db
python figurex_db\get_bioc.py -d %database_file% -b %bioc_dir%
python figurex_db\get_figure_url.py -d %database_file% -b %bioc_dir%
python figurex_db\get_figures.py -d %database_file% -f %bioc_dir%
python figurex_db\split_figures.py -d %database_file% -f %bioc_dir% -m %figure_separation_model%
