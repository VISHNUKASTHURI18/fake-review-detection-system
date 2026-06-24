import pandas as pd

df = pd.read_csv("fake reviews dataset.csv")

print(df.head())

print("\nColumns:")
print(df.columns)

print("\nLabels:")
print(df["label"].value_counts())