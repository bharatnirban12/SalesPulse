from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import numpy as np
import pickle
import os
import yaml

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

# --- UI DATA ENDPOINTS ---
@app.get("/api/data/forecast")
def get_forecast_data():
    file_path = "data/processed/forecast_output.csv"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/csv")
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.get("/api/data/training")
def get_training_data():
    file_path = "data/processed/featured_data.csv"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/csv")
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.get("/api/data/stores")
def get_stores_data():
    file_path = "data/raw/stores.csv"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/csv")
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.get("/api/config")
def get_config():
    file_path = "src/config/config.yaml"
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        return {"sparse_categories": [], "sparse_threshold": 0.7}

@app.get("/api/models")
def get_models():
    model_files = []
    if os.path.exists("models"):
        for f in os.listdir("models"):
            fp = os.path.join("models", f)
            if os.path.isfile(fp):
                size_kb  = os.path.getsize(fp) / 1024
                m_type   = "Sparse Pipeline" if "sparse" in f.lower() else "Dense XGBoost"
                model_files.append({"File": f, "Size": f"{size_kb:,.1f} KB", "Type": m_type})
    return model_files