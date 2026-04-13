import pandas as pd

print("1. Loading featured_data.csv...")
df = pd.read_csv("data/processed/featured_data.csv")

print("2. Compressing into featured_data.csv.zip...")
df.to_csv("data/processed/featured_data.csv.zip", compression="zip", index=False)

print("3. Done! The dataset is now compressed and ready to be pushed to GitHub.")
