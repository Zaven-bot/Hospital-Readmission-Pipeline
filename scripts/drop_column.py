# Purpose: Test if the dvc is actually picking up
# changes in data :)

import pandas as pd

df = pd.read_csv("data/processed/cleaned_data.csv")
df = df.drop(columns=["glyburide-metformin_Steady"], errors='ignore')  # or any column you want
df.to_csv("data/processed/cleaned_data.csv", index=False)