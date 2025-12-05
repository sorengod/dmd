import pandas as pd

def load_excel_file(path:str) -> pd.DataFrame:
    return pd.read_excel("DMD.xlsx")

class DataPreProcessor():
    def __init__(self, df:pd.DataFrame):
        self.df = df 
    
    def convert_col_to_datetime(self, col_name:str, date_format:str="%Y%m%d") -> pd.DataFrame:
        self.df[col_name] = pd.to_datetime(
        self.df[col_name].astype(str).str.zfill(8),  # ensure 8-digit YYYYMMDD
        format=date_format,
        errors="coerce"
        )
        return self.df

data = DataPreProcessor(load_excel_file("DMD.xlsx"))

data.convert_col_to_datetime("Date")