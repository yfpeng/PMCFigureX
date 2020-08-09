from collections import Counter
import pandas as pd
import tabulate


def pprint_counter(counter: Counter, sort_key: bool = False, sep: str = '\t', use_tabulate=True):
    if not sort_key:
        itr = counter.most_common()
    else:
        itr = sorted(counter.items(), key=lambda s: s[0])

    total = sum(counter.values())
    data = []
    for k, v in itr:
        p = '%.1f' % (v / total * 100)
        data.append({'key': k, 'value': v, '%': p})

    df = pd.DataFrame(data)
    if use_tabulate:
        s = tabulate.tabulate(df, showindex=False, headers=df.columns, tablefmt="plain", )
        print(s)
    else:
        for k, v, p in zip(df['key'], df['value'], df['%']):
            print(f'{k}{sep}{v}{sep}{p}%')
