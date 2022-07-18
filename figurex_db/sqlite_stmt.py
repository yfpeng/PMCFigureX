sql_create_articles_table = """
CREATE TABLE IF NOT EXISTS Articles (
    pmcid       TEXT PRIMARY KEY,
    pmid        TEXT,
    doi         TEXT,
    has_bioc    INTEGER,
    has_medline INTEGER,
    has_figure  INTEGER,
    insert_time TEXT
);
"""

sql_create_figures_table = """
CREATE TABLE IF NOT EXISTS Figures (
    pmcid         TEXT,
    figure_name   TEXT,
    width         INTEGER,
    height        INTEGER,
    has_subfigure INTEGER,
    insert_time   TEXT,
    PRIMARY KEY (pmcid, figure_name)
);
"""

sql_create_subfigures_table = """
CREATE TABLE IF NOT EXISTS Subfigures (
    pmcid       TEXT,
    figure_name TEXT,
    xtl         INTEGER,
    ytl         INTEGER,
    xbr         INTEGER,
    ybr         INTEGER
    label       TEXT,
    labeler     TEXT,
    insert_time TEXT
);
"""

sql_insert_articles = """
INSERT INTO Articles(pmcid, pmid, doi, insert_time) 
VALUES      (?,?,?,?);
"""

sql_select_articles = """
SELECT pmid
FROM   Articles;
"""

sql_select_empty_bioc = """
SELECT pmcid, pmid 
FROM   Articles 
WHERE  has_bioc IS NULL 
AND    pmid IS NOT NULL;
"""

sql_update_articles = """
UPDATE Articles 
SET    has_bioc = ? 
WHERE  pmcid = ?;
"""

sql_select_new_bioc = """
SELECT      DISTINCT t1.pmcid
FROM        Articles AS t1
LEFT JOIN   Figures AS t2
ON          t1.pmcid = t2.pmcid
WHERE       t2.pmcid IS NULL 
AND         t1.has_bioc = 1
AND         (t1.has_figure == 1 OR t1.has_figure IS NULL);
"""

sql_insert_figure = """
INSERT INTO Figures(pmcid, figure_name, insert_time) 
VALUES      (?,?,?);
"""

sql_update_has_figure1 = """
UPDATE Articles
SET    has_figure = 1
WHERE  pmcid IN (
    SELECT    a.pmcid
    FROM      Articles AS a
    LEFT JOIN Figures AS f
    ON        a.pmcid = f.pmcid
    WHERE     f.pmcid IS NOT NULL
    AND       a.has_bioc = 1);
"""

sql_update_has_figure0 = """
UPDATE Articles
SET    has_figure = 0
WHERE  pmcid IN (
    SELECT    a.pmcid
    FROM      Articles AS a
    LEFT JOIN Figures AS f
    ON        a.pmcid = f.pmcid
    WHERE     f.pmcid IS NULL
    AND       a.has_bioc = 1);
"""

sql_get_empty_figures = """
SELECT pmcid, figure_name
FROM   Figures
WHERE  width IS NULL;
"""

sql_update_figure_size = """
UPDATE Figures
SET    width=?, height=?
WHERE  pmcid=? AND figure_name=?
"""

sql_select_empty_subfigurejsonfiles = """
SELECT      t1.pmcid, t1.figure_name
FROM        Figures t1
LEFT JOIN   Subfigures t2
ON          t1.pmcid = t2.pmcid
AND         t1.figure_name = t2.figure_name
WHERE       t2.figure_name IS NULL
AND         t1.width IS NOT NULL;
"""

sql_insert_subfigure = """
INSERT INTO Subfigures(pmcid, figure_name, xtl, ytl, xbr, ybr, labeler, insert_time) 
VALUES      (?,?,?,?,?,?,?,?);
"""

sql_select_subfigure = """
SELECT pmcid, figure_name, xtl, ytl, xbr, ybr
FROM   Subfigures;
"""

sql_update_has_subfigure1 = """
UPDATE Figures
SET    has_subfigure = 1
WHERE  (pmcid, figure_name) IN (
    SELECT      t1.pmcid, t1.figure_name
    FROM        Figures t1
    LEFT JOIN   Subfigures t2
    ON          t1.pmcid = t2.pmcid
    AND         t1.figure_name = t2.figure_name
    WHERE       t2.figure_name IS NOT NULL
    AND         t1.width IS NOT NULL);
"""

sql_update_has_subfigure0 = """
UPDATE Figures
SET    has_subfigure = 0
WHERE  (pmcid, figure_name) IN (
    SELECT      t1.pmcid, t1.figure_name
    FROM        Figures t1
    LEFT JOIN   Subfigures t2
    ON          t1.pmcid = t2.pmcid
    AND         t1.figure_name = t2.figure_name
    WHERE       t2.figure_name IS NULL
    AND         t1.width IS NOT NULL);
"""

sql_select_figure = """
SELECT pmcid, figure_name, width, height
FROM   Figures
WHERE  width IS NOT NULL;
"""