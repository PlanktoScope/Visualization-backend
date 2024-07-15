
import pandas as pd

from utils import CustomDataFrame

def load_dataframe(path):
    # Load a TSV (Tab Separated Values) file into a pandas DataFrame
    tsv = pd.read_csv(path, sep='\t')
    
    # Initialize a CustomDataFrame object with the loaded data and the file path
    df = CustomDataFrame(tsv, path=path)
    # Drop the first row of the DataFrame
    df = df.drop(0)
    # The following line (commented out) would display the first 10 rows of the DataFrame
    #df.head(10)
    # Initialize an empty list to store columns of interest
    metadatas_of_interest=[]
    
    # Iterate through each column in the original DataFrame
    for col in tsv.columns:
        # Check if the first row of the column is marked with '[f]', indicating it should be treated as numeric
        if tsv[col][0] == '[f]':
            # Convert the column to numeric type
            df[col] = pd.to_numeric(df[col])
            # Add the column to the list of metadatas of interest if it contains 'object_', but not 'id' or 'label'
            if("object_" in col and "id" not in col and "label" not in col):
                metadatas_of_interest.append(col)

    
    print(f"DataFrame loaded from {df.path}")
    return df,len(df),metadatas_of_interest

# Exemple d'utilisation
if __name__ == '__main__':
    df,number_of_object = load_dataframe('C:\\Users\\luffy\\.node-red\\data\\BTS2023_S2\\ecotaxa_export.tsv')
    print(df.head(10))
    print(f"Number of object : {number_of_object}")