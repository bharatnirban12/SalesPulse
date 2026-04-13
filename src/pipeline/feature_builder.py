import pandas as pd
import numpy as np


class FeatureBuilder:
    def __init__(self):
        self.data_path = "data/processed/featured_data.csv.zip"
        self.df = pd.read_csv(self.data_path)
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.global_min_date = self.df["date"].min()

    def get_history(self, store_nbr, family):
        df = self.df[
            (self.df["store_nbr"] == store_nbr) &
            (self.df["family"] == family)
        ].sort_values("date")
        return df

    def create_features(self, store_nbr, family, prediction_date):
        prediction_date = pd.to_datetime(prediction_date)

        history = self.df[
            (self.df["store_nbr"] == store_nbr) &
            (self.df["family"] == family)
        ].sort_values("date")

        history = history[history["date"] < prediction_date]

        if history.empty:
            raise ValueError(
                f"No historical data found for store_nbr={store_nbr}, family='{family}' "
                f"before {prediction_date.date()}"
            )

        day_of_week  = prediction_date.dayofweek
        month        = prediction_date.month
        day_of_month = prediction_date.day
        week_of_year = prediction_date.isocalendar()[1]
        time_index   = (prediction_date - self.global_min_date).days
        is_weekend   = int(day_of_week in [5, 6])

        sales_series = history.set_index("date")["sales"].sort_index()

        def get_lag(n):
            lag_date = prediction_date - pd.Timedelta(days=n)
            if lag_date in sales_series.index:
                return sales_series[lag_date]
            past = sales_series[sales_series.index <= lag_date]
            return float(past.iloc[-1]) if not past.empty else 0.0

        dales_lag_1  = get_lag(1)
        dales_lag_7  = get_lag(7)
        dales_lag_14 = get_lag(14)
        dales_lag_28 = get_lag(28)

        def rolling_mean(window):
            vals = sales_series.iloc[-window:]
            return float(vals.mean()) if len(vals) > 0 else 0.0

        def rolling_std(window):
            vals = sales_series.iloc[-window:]
            return float(vals.std()) if len(vals) > 1 else 0.0

        roliing_mean_7  = rolling_mean(7)
        rolling_std_7   = rolling_std(7)
        rolling_mean_14 = rolling_mean(14)
        rolling_mean_30 = rolling_mean(30)

        # Take the last historical row — it already has ALL columns the model needs
        # (city, state, cluster, transactions, type, locale, etc.)
        # We only overwrite the features that change per prediction date.
        feature_row = history.iloc[-1:].copy()

        # Drop target and date columns (model doesn't use them)
        drop_cols = [c for c in ["sales", "date"] if c in feature_row.columns]
        feature_row = feature_row.drop(columns=drop_cols)

        # Overwrite time features for the new prediction date
        feature_row["day_of_week"]  = day_of_week
        feature_row["day_of_month"] = day_of_month
        feature_row["week_of_year"] = week_of_year
        feature_row["time_index"]   = time_index
        feature_row["is_weekend"]   = is_weekend

        # Handle monthx vs month column name (typo in feature_engineering.py)
        if "monthx" in feature_row.columns:
            feature_row["monthx"] = month
        elif "month" in feature_row.columns:
            feature_row["month"] = month

        # Overwrite lag and rolling features
        feature_row["dales_lag_1"]     = dales_lag_1
        feature_row["dales_lag_7"]     = dales_lag_7
        feature_row["dales_lag_14"]    = dales_lag_14
        feature_row["dales_lag_28"]    = dales_lag_28
        feature_row["roliing_mean_7"]  = roliing_mean_7
        feature_row["rolling_std_7"]   = rolling_std_7
        feature_row["rolling_mean_14"] = rolling_mean_14
        feature_row["rolling_mean_30"] = rolling_mean_30

        return feature_row