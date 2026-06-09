from pathlib import Path
import re
import pandas as pd
import pm4py

RAW_LOG = Path("data/raw/LogFilesProductWarmupFilter/Exp10Run1.txt")
OUTPUT_CSV = Path("data/processed/Exp10Run1_clean.csv")
OUTPUT_XES = Path("outputs/xes/Exp10Run1_clean.xes")

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_XES.parent.mkdir(parents=True, exist_ok=True)

if not RAW_LOG.exists():
    raise FileNotFoundError(f"File not found: {RAW_LOG}")

# Load file
df = pd.read_csv(RAW_LOG, sep=None, engine="python")
df.columns = [col.strip() for col in df.columns]

print("Original shape:", df.shape)
print("Columns:", df.columns.tolist())

# Required columns
required = ["productIDStr", "event", "timeStamp"]
missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Keep only events with valid product cases
df = df[df["productIDStr"].notna()]
df = df[df["productIDStr"].astype(str).str.strip() != ""]
df = df[df["productIDStr"].astype(str).str.strip() != "(?)"]

# Remove empty activities/timestamps
df = df[df["event"].notna()]
df = df[df["timeStamp"].notna()]

# Add experiment and run identifiers from filename
match = re.search(r"Exp(\d+)Run(\d+)", RAW_LOG.name)
if match:
    df["experiment_id"] = int(match.group(1))
    df["run_id"] = int(match.group(2))
else:
    df["experiment_id"] = None
    df["run_id"] = None

# Convert timestamp
# If timestamp is numeric simulation time, convert it to artificial datetime.
# If timestamp is already datetime-like, parse it normally.
time_numeric = pd.to_numeric(df["timeStamp"], errors="coerce")

if time_numeric.notna().mean() > 0.9:
    df["time:timestamp"] = pd.Timestamp("2020-01-01") + pd.to_timedelta(time_numeric, unit="s")
else:
    df["time:timestamp"] = pd.to_datetime(df["timeStamp"], errors="coerce")

df = df[df["time:timestamp"].notna()]

# Rename for PM4Py
df["case:concept:name"] = df["productIDStr"].astype(str)
df["concept:name"] = df["event"].astype(str)

# Optional resource column
if "vehicle" in df.columns:
    df["org:resource"] = df["vehicle"].astype(str)
elif "vehicleType" in df.columns:
    df["org:resource"] = df["vehicleType"].astype(str)
else:
    df["org:resource"] = "NA"

# Sort events
df = df.sort_values(["case:concept:name", "time:timestamp"])

# Save cleaned CSV
df.to_csv(OUTPUT_CSV, index=False)

# Format for PM4Py
event_log_df = pm4py.format_dataframe(
    df,
    case_id="case:concept:name",
    activity_key="concept:name",
    timestamp_key="time:timestamp"
)

# Export XES
pm4py.write_xes(event_log_df, str(OUTPUT_XES))

# Basic summary
print("\nCleaned shape:", df.shape)
print("Number of cases:", df["case:concept:name"].nunique())
print("Number of events:", len(df))
print("Number of activities:", df["concept:name"].nunique())
print("Cleaned CSV saved to:", OUTPUT_CSV)
print("XES saved to:", OUTPUT_XES)

print("\nTop activities:")
print(df["concept:name"].value_counts().head(10))