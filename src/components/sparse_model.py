import os
import pickle
import pandas as pd
import numpy as np

from xgboost import XGBClassifier, XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer


class SparseModel:

    def __init__(self):
        self.data_path = "data/processed/featured_data.csv"
        self.model_path = "models/sparse_model.pkl"

        os.makedirs("models", exist_ok=True)

    def load_data(self):
        df = pd.read_csv(self.data_path)
        return df

    def prepare_data(self, df):

        df["is_sale"] = (df["sales"] > 0).astype(int)

        drop_cols = ["date", "sales"]

        X = df.drop(columns=drop_cols + ["is_sale"])
        y_cls = df["is_sale"]

        df_reg = df[df["sales"] > 0]

        X_reg = df_reg.drop(columns=drop_cols + ["is_sale"])
        y_reg = np.log1p(df_reg["sales"])

        return X, y_cls, X_reg, y_reg

    def train(self):

        df = self.load_data()

        X, y_cls, X_reg, y_reg = self.prepare_data(df)

        # Identify column types
        cat_cols = X.select_dtypes(include=["object"]).columns.tolist()
        num_cols = X.select_dtypes(exclude=["object"]).columns.tolist()

        print(f"Categorical columns: {cat_cols}")
        print(f"Numerical columns: {num_cols}")

        # Preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
            ]
        )

        print("Training classifier...")
        clf = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        clf_pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", clf)
        ])

        clf_pipeline.fit(X, y_cls)

        print("Training regressor...")
        reg = XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        reg_pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", reg)
        ])

        reg_pipeline.fit(X_reg, y_reg)

        with open(self.model_path, "wb") as f:
            pickle.dump({
                "classifier": clf_pipeline,
                "regressor": reg_pipeline
            }, f)

        print("Sparse model saved!")

    def predict(self, features):

        with open(self.model_path, "rb") as f:
            models = pickle.load(f)

        clf_pipeline = models["classifier"]
        reg_pipeline = models["regressor"]

        prob = clf_pipeline.predict(features)[0]

        if prob == 0:
            return 0.0

        pred_log = reg_pipeline.predict(features)
        return float(np.expm1(pred_log)[0])


if __name__ == "__main__":
    sm = SparseModel()
    sm.train()


