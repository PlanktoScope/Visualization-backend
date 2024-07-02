
import pandas as pd

def load_dataframe(path):
    tsv = pd.read_csv(path, sep='\t')

    df = tsv.copy()
    #drop first row
    df = df.drop(0)
    #df.head(10)
    for col in tsv.columns:
        if tsv[col][0] == '[f]':
            df[col] = pd.to_numeric(df[col])
    
    print(df.head(3))
    return df,len(df)