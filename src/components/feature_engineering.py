import os 
import pandas as pd 

class FeatureEngineering:
    def __init__(self):
        self.input_path = "data/processed/clean_data.csv"
        self.output_path = "data/processed/featured_data.csv"

    def load_data(self):
        print("Loading clean data...")
        df = pd.read_csv(self.input_path)
        df["date"] = pd.to_datetime(df["date"])
        return df

    def create_time_features(self, df):
        print("Creating time-based features...")
        df["day_of_week"] = df["date"].dt.dayofweek
        df["month"] = df["date"].dt.month
        df["day_of_month"] = df["date"].dt.day
        df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
        df["time_index"] = (df["date"] - df["date"].min()).dt.days

        df["is_weekend"] = df["day_of_week"].isin([5,6]).astype(int)

        return df

    def create_lag_features(self, df):
        print("Creating lag features...")

        df = df.sort_values(by=["store_nbr", "family","date"])

        for lag in [1, 7, 14, 28]:
            df[f"dales_lag_{lag}"] = df.groupby(["store_nbr", "family"])["sales"].shift(lag)
        
        return df


    def create_rolling_features(self, df):
        print("Creating rolling features...")

        df = df.sort_values(by= ["store_nbr", "family", "date"])

        df["roliing_mean_7"] = (
            df.groupby(["store_nbr", "family"])["sales"]
            .shift(1)
            .rolling(window=7)
            .mean()
        )
        
        df["rolling_std_7"] = (
            df.groupby(["store_nbr", "family"])["sales"]
            .shift(1)
            .rolling(window=7)
            .std()
        )

        df["rolling_mean_14"] = (
            df.groupby(["store_nbr", "family"])["sales"]
            .shift(1)
            .rolling(14)
            .mean()
        )

        df["rolling_mean_30"] = (
            df.groupby(["store_nbr", "family"])["sales"]
            .shift(1)
            .rolling(30)
            .mean()
        )   

        return df


    def handle_missing_after_features(self, df):
        print("Handling missing values after feature creation...")

        df = df.copy()  

        df = df.dropna()

        df.loc[:, "sales"] = df["sales"].clip(
            lower=0,
            upper=df["sales"].quantile(0.99)
        )

        return df

    def save_data(self, df):
        df.to_csv(self.output_path, index=False)
        print(f"Featured data saved at {self.output_path}")

    def run(self):
        df = self.load_data()

        df = self.create_time_features(df) 
        df = self.create_lag_features(df) 
        df = self.create_rolling_features(df)
        df = self.handle_missing_after_features(df)
        
        self.save_data(df)           

if __name__ == "__main__":
    fe = FeatureEngineering()
    fe.run()

