import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def load_data_from_google_sheets(json_file, sheet_name):
    """
    Reads data from a Google Sheet and returns a pandas DataFrame
    """
    creds = Credentials.from_service_account_file(
        json_file,
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    
    gc = gspread.authorize(creds)
    sh = gc.open(sheet_name)
    worksheet = sh.sheet1
    
    # Read all the data from the sheet
    data = worksheet.get_all_records()
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    return df

def clean_data(df):
    """
    Basic data cleaning function
    """
    df = df.dropna()  # remove lines with missing values
    # Convert columns to appropriate data types
    if 'Quantity' in df.columns:
        df['Quantity'] = df['Quantity'].astype(int)
    if 'Price' in df.columns:
        df['Price'] = df['Price'].astype(float)
    
    return df
