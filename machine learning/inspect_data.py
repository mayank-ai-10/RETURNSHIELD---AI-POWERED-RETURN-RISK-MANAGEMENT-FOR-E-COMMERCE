import pandas as pd

# Load dataset
df = pd.read_csv("data/return_risk_dataset.csv")

print("Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nReturn distribution:")
print(df["is_returned"].value_counts())

print("\nReturn percentage:")
print(df["is_returned"].value_counts(normalize=True) * 100)

print("\nBasic statistics:")
print(df.describe())