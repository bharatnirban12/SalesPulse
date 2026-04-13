import numpy as np

def add_confidence_intervals(df, scale_factor=0.2):

    df["lower_bound"] = np.maximum(0, df["prediction"] * (1 - scale_factor))
    df["upper_bound"] = df["prediction"] * (1 + scale_factor)

    return df