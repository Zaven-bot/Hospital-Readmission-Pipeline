# Purpose: Test if the dvc is actually picking up
# changes in data :)

import pandas as pd

df = pd.read_csv("data/processed/cleaned_data.csv")
df = df.drop(columns=["payer_code"], errors='ignore')  # or any column you want
df.to_csv("data/processed/cleaned_data.csv", index=False)