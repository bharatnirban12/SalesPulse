from fastapi import FastAPI
import pandas as pd
import numpy as np
import pickle

from app.schema import PredictionInput, ForecastInput, BatchForecastInput
from src.pipeline.feature_builder import FeatureBuilder
from src.pipeline.forecast_engine import ForecastEngine
from src.pipeline.router import ModelRouter
from src.utils.confidence import add_confidence_intervals


# Initialize app
app = FastAPI()

# Initialize pipelines
feature_builder = FeatureBuilder()
forecast_engine = ForecastEngine()
router = ModelRouter()

# Home endpoint
@app.get("/")
def home():
    return {"message": "Time Series Forecasting API is running"}


# SINGLE PREDICTION
@app.post("/predict")
def predict(data: PredictionInput):

    try:
        features = feature_builder.create_features(
            store_nbr=data.store_nbr,
            family=data.family,
            prediction_date=data.date
        )

        prediction = router.predict(features)

        return {"prediction": prediction}

    except Exception as e:
        return {"error": str(e)}


# MULTI-DAY FORECAST
@app.post("/forecast")
def forecast(data: ForecastInput):

    try:
        df = forecast_engine.forecast(
            data.store_nbr,
            data.family,
            data.start_date,
            data.weeks
        )

        df = add_confidence_intervals(df)

        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}

# FAST BATCH FORECAST
@app.post("/batch_forecast")
def get_batch_forecast(data: BatchForecastInput):

    try:
        df = pd.read_csv("data/processed/forecast_output.csv")
        
        if data.weeks:
            days = data.weeks * 7
            df["date"] = pd.to_datetime(df["date"])
            start_date = df["date"].min()
            end_date = start_date + pd.Timedelta(days=days-1)
            df = df[df["date"] <= end_date]
            
            # Summary mode: aggregate total sales per date
            if data.summary:
                df = df.groupby("date")["prediction"].sum().reset_index()
            else:
                # Group by store, family, and then date
                df = df.sort_values(by=["store_nbr", "family", "date"])
            
            df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        # Apply limiting
        if not data.summary and len(df) > data.limit:
            df = df.head(data.limit)

        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}