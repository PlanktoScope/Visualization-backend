
import os
import pandas as pd
import zipfile

def find_tsv_files(path):
    # Initialize an empty list to store the paths of TSV files
    tsv_files = []
    
    # Iterate through the directory tree
    for root, dirs, files in os.walk(path):
        for file in files:
            # Check if the file is a TSV file
            if file.endswith('.tsv'):
                # Add the path of the TSV file to the list
                tsv_files.append(os.path.join(root, file))

            if file.endswith('.zip'):
                # explore the zip file
                with zipfile.ZipFile(os.path.join(root, file), 'r') as zip_ref:
                    for inner_file in zip_ref.namelist():
                        if inner_file.endswith('.tsv'):
                            # Add the path of the TSV file to the list
                            tsv_files.append(os.path.join(root, file) + ':' + inner_file)
    
    return tsv_files

def load_dataframe(path):
    # Initialize a CustomDataFrame object with the path
    df = CustomDataFrame(path=path)
    
    # To lower case all column names
    df.columns = df.columns.str.lower()
    
    # Drop the first row of the DataFrame
    types = df.iloc[0]
    df = df.drop(0)
    
    # Initialize an empty list to store columns of interest
    metadatas_of_interest = []
    
    # Iterate through each column in the DataFrame
    for col in df.columns:
        # Check if the first row of the column is marked with '[f]', indicating it should be treated as numeric
        if types[col] == '[f]':
            # Convert the column to numeric type
            df[col] = pd.to_numeric(df[col])
            # Add the column to the list of metadatas of interest if it contains 'object_', but not 'id' or 'label'
            if "object_" in col and "id" not in col and "label" not in col:
                metadatas_of_interest.append(col)

    return df, len(df), metadatas_of_interest

class CustomDataFrame(pd.DataFrame):
    _metadata = ['path', 'name','zip']
    
    def __init__(self, *args, path=None, **kwargs):
        if path:
            if 'zip:' in path:
                zip_path, inner_path = path.split('zip:', 1)
                zip_path=zip_path+'zip'
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    with zip_ref.open(inner_path) as file:
                        # Read the TSV file from the ZIP archive
                        super().__init__(pd.read_csv(file, sep='\t', *args, **kwargs))
                self.zip = True
            else:
                # Read the TSV file directly
                super().__init__(pd.read_csv(path, sep='\t', *args, **kwargs))
                self.zip = False
            self.path = path
            self.name = os.path.basename(path)
        else:
            super().__init__(*args, **kwargs)
            self.path = None
            self.name = None
            self.zip = False
    
    @property
    def _constructor(self):
        return CustomDataFrame




if __name__ == "__main__":
    # Example usage
    tsv_files=find_tsv_files('C:\\Users\\luffy\\.node-red\\data\\export')
    print(f"Found {len(tsv_files)} TSV files:")
    for file in tsv_files:
        print(file)
