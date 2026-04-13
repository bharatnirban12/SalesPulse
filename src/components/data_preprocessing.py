import os
import pandas as pd


class DataPreprocessing:
    def __init__(self):
        self.input_path = "data/processed/merged_data.csv"
        self.output_path = "data/processed/clean_data.csv"

    def load_data(self):
        print("Loading merged data...")
        df = pd.read_csv(self.input_path)
        return df

    def preprocess(self, df):
        print("Starting preprocessing...")

        # Convert data column
        df['data'] = pd.to_datetime(df["date"])

        # Sort by time
        df = df.sort_values(by=["store_nbr", "family","date"])

        # Handle missing values
        
        if "transactions" in df.columns:
            df["transactions"] = df["transactions"].fillna(0)

        if "dcoilwtico" in df.columns:
            df["dcoilwtico"] = df["dcoilwtico"].ffill()

        holiday_cols = ["types", "locale", "locale_name", "description", "transferred"]
        for col in holiday_cols:
            if col in df.columns:
                df[col] = df[col].fillna("None")



        # Drop duplicates
        df = df.drop_duplicates()

        # Basic checks
        df = df[df["sales"].notna()]

        return df

    def save_data(self, df):
        df.to_csv(self.output_path, index=False)
        print(f"Clean data saved at {self.output_path}")

    def run(self):
        df = self.load_data()
        df = self.preprocess(df)
        self.save_data(df)


if __name__ == "__main__":
    processor = DataPreprocessing()
    processor.run()



