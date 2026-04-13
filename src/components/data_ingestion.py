import os 
import pandas as pd
from dataclasses import dataclass

# CONFIG CLASS

@dataclass
class DataIngestion:
    def __init__(self):
        self.raw_data_path: str = "data/raw"
        self.processed_data_path = "data/processed"

        os.makedirs(self.processed_data_path, exist_ok = True)

    def load_data(self):
        print("Loading data from raw directory")
        
        train = pd.read_csv(os.path.join(self.raw_data_path, "train.csv"))
        stores = pd.read_csv(os.path.join(self.raw_data_path, "stores.csv"))
        transactions = pd.read_csv(os.path.join(self.raw_data_path, "transactions.csv"))
        holidays = pd.read_csv(os.path.join(self.raw_data_path, "holidays_events.csv"))
        oil = pd.read_csv(os.path.join(self.raw_data_path, "oil.csv"))

        return train, stores, transactions, holidays, oil

    def merge_data(self):
        train, stores, transactions, holidays, oil = self.load_data()

        print("Merging datasets...")

        # Merge stores
        df = pd.merge(train, stores, on="store_nbr", how="left")

        # Merge transactions
        df = pd.merge(df, transactions, on=["date", "store_nbr"], how="left")

        # Merge holidays
        holidays = holidays.drop_duplicates(subset=["date"])
        df = df.merge(holidays, on="date", how="left")
        
        # Merge oil
        df = pd.merge(df, oil, on="date", how="left")

        return df 

    def save_data(self, df):
        output_path = os.path.join(self.processed_data_path, "merged_data.csv")
        df.to_csv(output_path, index=False)
        print(f"Data saved at {output_path}")

    def run(self):
        df = self.merge_data()
        self.save_data(df)

if __name__ == "__main__":
    ingestor = DataIngestion()
    ingestor.run()           