import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import numpy as np
import pickle

from src.pipeline.feature_builder import FeatureBuilder
from src.pipeline.router import ModelRouter


class ForecastEngine:
    def __init__(self):
        self.router = ModelRouter()
        self.feature_builder = FeatureBuilder()

    # SINGLE FORECAST (for API /forecast)
    def forecast(self, store_nbr, family, start_date, weeks=1):

        days = weeks * 7
        results = []

        current_date = pd.to_datetime(start_date)

        # Get historical data
        history_df = self.feature_builder.get_history(store_nbr, family).copy()

        for i in range(days):

            next_date = current_date + pd.Timedelta(days=1)

            # Build features
            features = self.feature_builder.create_features(
                store_nbr,
                family,
                next_date
            )

            # Predict using router (already handles np.expm1 and sparse/dense switching)
            pred = self.router.predict(features)

            # Save result
            results.append({
                "date": next_date,
                "prediction": pred
            })

            # Update history
            new_row = history_df.iloc[-1:].copy()
            new_row["date"] = next_date
            new_row["sales"] = pred

            history_df = pd.concat([history_df, new_row], ignore_index=True)

            current_date = next_date

        return pd.DataFrame(results)

    # BATCH FORECAST (optimized)
    def forecast_batch(self, start_date, weeks=1):

        days = weeks * 7
        current_date = pd.to_datetime(start_date)

        df = self.feature_builder.df.copy()
        
        unique_pairs = df[["store_nbr", "family"]].drop_duplicates()

        history_df = df.copy()

        all_results = []

        for i in range(days):

            next_date = current_date + pd.Timedelta(days=1)

            batch_features = []

            latest_rows = (
                history_df
                .sort_values("date")
                .groupby(["store_nbr", "family"])
                .tail(1)
            )

            for _, row in latest_rows.iterrows():

                features = row.copy()
                features["date"] = next_date

                if "sales" in features:
                    features = features.drop(labels=["sales"])

                batch_features.append(features)

            batch_df = pd.DataFrame(batch_features)

            # Predict using router (handles np.expm1 and switching)
            preds = self.router.predict(batch_df)

            batch_df["prediction"] = preds

            # Save results
            result_df = batch_df[["store_nbr", "family", "date", "prediction"]]
            all_results.append(result_df)

            # Update history
            batch_df["sales"] = preds
            history_df = pd.concat([history_df, batch_df], ignore_index=True)

            current_date = next_date

        final_df = pd.concat(all_results, ignore_index=True)

        return final_df