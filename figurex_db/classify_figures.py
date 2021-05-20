"""
Usage:
    script.py [options] -f figure_folder -m model_file -s source_file -o dest_file

Options:
    -f <directory>      Figure folder
    -m <file>           Model path
    -s <file>           Source figure file
    -o <file>           Prediction figure file
    --history <file>    History prediction file
    --overwrite         Overwrite
"""

import os
from pathlib import Path

import docopt
import numpy as np
import pandas as pd
from keras.applications import densenet
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


def image_exists(fullpath):
    return os.path.exists(fullpath) and os.path.isfile(fullpath)


def detect_normal_cxr_ct(model_pathname, src, dest, image_dir, x_col='filename', history=None,
                         overwrite: bool=True):
    if not overwrite and dest.exists():
        print('%s exists.' % dest)
        return

    total_df = pd.read_csv(src)
    if history is not None:
        history_df = pd.read_csv(history)
        df = total_df.merge(history_df, how='outer', indicator=True).loc[lambda x: x['_merge'] == 'left_only']
        print(len(total_df), len(history_df), len(df))
    else:
        df = total_df

    if len(df) != 0:
        df = df.reset_index(drop=True)
        df = df.assign(full_path=df[x_col].apply(lambda x: os.path.join(image_dir, x)))
        df = df[df["full_path"].apply(image_exists)]
        df = df.reset_index(drop=True)
        datagen = ImageDataGenerator(preprocessing_function=densenet.preprocess_input)
        generator = datagen.flow_from_dataframe(
            dataframe=df,
            target_size=(214, 214),
            x_col='full_path',
            class_mode=None,
            batch_size=32,
            shuffle=False
        )

        print('Load from %s' % model_pathname)
        model = load_model(model_pathname)
        y_score = model.predict_generator(generator, verbose=1)

        columns = ['ct', 'cxr', 'nature']
        y_pred = np.argmax(y_score, axis=1)
        predictions = [columns[x] for x in y_pred]
        assert len(predictions) == len(df), '{} vs {}'.format(len(predictions), len(df))

        df_score = pd.DataFrame(y_score, columns=columns)
        df_score = df_score.assign(prediction=predictions)

        df = pd.concat([df, df_score], axis=1)
        df = df.drop(['full_path'], axis=1)

    if history is not None:
        df = df.drop(['_merge'], axis=1)
        print(history_df.columns, df.columns)
        df = pd.concat([history_df, df], axis=0)

    df.to_csv(dest, index=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    if args['--history'] is not None:
        history = Path(args['--history'])
    else:
        history = None

    image_dir = Path(args['-f'])
    detect_normal_cxr_ct(model_pathname=args['-m'],
                         image_dir=Path(args['-f']),
                         src=Path(args['-s']),
                         dest=Path(args['-o']),
                         x_col='figure path',
                         history=history,
                         overwrite=args['--overwrite'])
