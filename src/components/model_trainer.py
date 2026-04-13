import os
import pandas as pd
import numpy as np
import pickle

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from xgboost import XGBRegressor


class ModelTrainer:
    def __init__(self):
        self.data_path = "data/processed/featured_data.csv"
        self.model_path = "models/model.pkl"

        os.makedirs("models", exist_ok=True)


    # Load Data
    def load_data(self):
        print("Loading featured data...")
        df = pd.read_csv(self.data_path)
        df["date"] = pd.to_datetime(df["date"])
        return df

    # Time-based Split
    def train_test_split(self, df):
        print("Splitting data (time-based)...")

        df = df.sort_values("date")

        split_date = "2017-01-01"

        train = df[df["date"] < split_date]
        test = df[df["date"] >= split_date]

        return train, test

    # Feature Preparation
    def prepare_features(self, train, test):
        print("Preparing features...")

        drop_cols = ["date", "sales"]

        X_train = train.drop(columns=drop_cols)
        y_train = np.log1p(train["sales"])

        X_test = test.drop(columns=drop_cols)
        y_test = np.log1p(test["sales"])

        # Identify column types
        cat_cols = X_train.select_dtypes(include=["object"]).columns.tolist()
        num_cols = X_train.select_dtypes(exclude=["object"]).columns.tolist()

        print(f"Categorical columns: {cat_cols}")
        print(f"Numerical columns: {num_cols}")

        # Preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
            ]
        )

        return X_train, X_test, y_train, y_test, preprocessor

    # Evaluation
    def evaluate(self, y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        return mae, rmse

    # Train Models
    def train_models(self, X_train, y_train, X_test, y_test, preprocessor):
        print("\nTraining XGBoost...")

        xgb_pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=0.1,
                reg_lambda=1.5,
                random_state=42
            ))
        ])

        xgb_pipeline.fit(X_train, y_train)
        preds_xgb = np.expm1(xgb_pipeline.predict(X_test))
        y_test_actual = np.expm1(y_test)

        mae_xgb, rmse_xgb = self.evaluate(y_test_actual, preds_xgb)

        print(f"XGB MAE: {mae_xgb}")
        print(f"XGB RMSE: {rmse_xgb}")

        return xgb_pipeline

    def save_model(self, model):
        with open(self.model_path, "wb") as f:
            pickle.dump(model, f)

        print(f"Model saved at {self.model_path}")


    def run(self):
        df = self.load_data()

        train, test = self.train_test_split(df)

        X_train, X_test, y_train, y_test, preprocessor = self.prepare_features(train, test)

        model = self.train_models(X_train, y_train, X_test, y_test, preprocessor)

        self.save_model(model)


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run()