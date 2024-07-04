
import pandas as pd

class CustomDataFrame(pd.DataFrame):
    _metadata = ['path']
    
    def __init__(self, *args, path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
    
    @property
    def _constructor(self):
        return CustomDataFrame

def load_dataframe(path):
    tsv = pd.read_csv(path, sep='\t')

    df = CustomDataFrame(tsv, path=path)
    #drop first row
    df = df.drop(0)
    #df.head(10)
    for col in tsv.columns:
        if tsv[col][0] == '[f]':
            df[col] = pd.to_numeric(df[col])
    
    print(f"DataFrame loaded from {df.path}")
    return df,len(df)

# Exemple d'utilisation
if __name__ == '__main__':
    df,number_of_object = load_dataframe('C:\\Users\\luffy\\.node-red\\data\\BTS2023_S2\\ecotaxa_export.tsv')
    print(df.head(10))
    print(f"Number of object : {number_of_object}")