import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
from src.pipeline.forecast_engine import ForecastEngine
from src.utils.confidence import add_confidence_intervals

# Initialize engine
engine = ForecastEngine()

print("Starting optimized batch forecast precompute...")

# Use the optimized forecast_batch method for all stores/families at once
final_df = engine.forecast_batch(
    start_date="2017-08-15",
    weeks=4
)

# Add confidence intervals
final_df = add_confidence_intervals(final_df)

# SAVE RESULTS
final_df.to_csv("data/processed/forecast_output.csv", index=False)

print(f"Forecast precomputed and saved! Total rows: {len(final_df)}")