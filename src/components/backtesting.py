import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


class Backtesting:
    def __init__(self):
        self.data_path = "data/processed/featured_data.csv"

    def load_data(self):
        df = pd.read_csv(self.data_path)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        return df

    def prepare_features(self, df):
        drop_cols = ["date", "sales"]

        X = df.drop(columns=drop_cols)
        y = df["sales"]

        cat_cols = X.select_dtypes(include=["object"]).columns.tolist()
        num_cols = X.select_dtypes(exclude=["object"]).columns.tolist()

        preprocessor = ColumnTransformer([
            ("num", "passthrough", num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
        ])

        return X, y, preprocessor

    def evaluate(self, y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        return mae, rmse

    def run_backtest(self):
        print("Running backtesting...")

        df = self.load_data()
        X, y, preprocessor = self.prepare_features(df)

        # rolling splits
        dates = df["date"].sort_values().unique()

        results = []

        for i in range(int(len(dates) * 0.6), len(dates) - 30, 30):

            train_dates = dates[:i]
            test_dates = dates[i:i+30]

            train_idx = df["date"].isin(train_dates)
            test_idx = df["date"].isin(test_dates)

            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            # Model pipeline
            model = Pipeline([
                ("preprocessor", preprocessor),
                ("model", XGBRegressor(
                    n_estimators=200,
                    max_depth=3,
                    learning_rate=0.03,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42
                ))
            ])

            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            mae, rmse = self.evaluate(y_test, preds)

            print(f"Window {i}: RMSE={rmse:.2f}")

            results.append(rmse)

        print("\nFinal Backtest Results:")
        print(f"Mean RMSE: {np.mean(results):.2f}")
        print(f"Std RMSE: {np.std(results):.2f}")

        return results


if __name__ == "__main__":
    bt = Backtesting()
    bt.run_backtest()