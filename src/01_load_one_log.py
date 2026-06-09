from pathlib import Path
import pandas as pd

RAW_LOG = Path("data/raw/LogFilesProductWarmupFilter/Exp10Run1.txt")

if not RAW_LOG.exists():
    raise FileNotFoundError(f"File not found: {RAW_LOG}")

# sep=None lets pandas guess whether the file is comma, semicolon, or tab separated
df = pd.read_csv(RAW_LOG, sep=None, engine="python")

# Clean column names
df.columns = [col.strip() for col in df.columns]

print("Loaded file:", RAW_LOG)
print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

# Basic checks for process mining columns
required_columns = ["productIDStr", "event", "timeStamp"]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    print("\nMissing required columns:", missing)
else:
    print("\nRequired process mining columns found.")
    print("Number of product cases:", df["productIDStr"].nunique())
    print("Number of events:", len(df))
    print("Number of activities:", df["event"].nunique())