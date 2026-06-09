from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/OutputWarmupFilter")
TABLES_DIR = Path("outputs/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

SELECTED_EXPERIMENTS = [10, 14, 23]
RUNS = range(1, 21)

all_outputs = []

def read_output_file(path: Path, experiment_id: int, run_id: int) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = [c.strip() for c in df.columns]

    df["experiment_id"] = experiment_id
    df["run_id"] = run_id

    return df

for exp in SELECTED_EXPERIMENTS:
    for run in RUNS:
        path = RAW_DIR / f"Exp{exp}Run{run}.txt"

        if not path.exists():
            print(f"Missing file, skipped: {path}")
            continue

        try:
            df_one = read_output_file(path, exp, run)
            all_outputs.append(df_one)
        except Exception as e:
            print(f"Failed to load {path}: {e}")

if not all_outputs:
    raise RuntimeError("No output files loaded. Check folder path.")

df = pd.concat(all_outputs, ignore_index=True)

# Columns expected from README
numeric_cols = [
    "waitingTimeRegion1",
    "waitingTimeRegion3",
    "totalWaitingTimeRegions",
    "travelTimeRegion1",
    "travelTimeRegion3",
    "totalTravelTimeRegions",
    "processingTimeRegion2",
    "totalQualityDecayRegions",
    "qualityDecayUntillDroppedOffRegion2",
    "qualityDecayUntillDroppedOffRegion3",
    "totalTimeInSystemInSeconds"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    else:
        print(f"Warning: column not found: {col}")

# Save combined output data
combined_path = TABLES_DIR / "selected_output_combined.csv"
df.to_csv(combined_path, index=False)

# Experiment-level KPI table
kpi_rows = []

for exp, group in df.groupby("experiment_id"):
    row = {
        "experiment": exp,
        "runs": group["run_id"].nunique(),
        "products": len(group)
    }

    for col in numeric_cols:
        if col in group.columns:
            row[f"mean_{col}"] = group[col].mean()
            row[f"median_{col}"] = group[col].median()

    kpi_rows.append(row)

kpi = pd.DataFrame(kpi_rows)

kpi_path = TABLES_DIR / "selected_kpi_by_experiment.csv"
kpi.to_csv(kpi_path, index=False)

# Smaller report-ready table
report_cols = [
    "experiment",
    "runs",
    "products",
    "mean_waitingTimeRegion1",
    "mean_waitingTimeRegion3",
    "mean_totalWaitingTimeRegions",
    "mean_totalTravelTimeRegions",
    "mean_totalTimeInSystemInSeconds",
    "mean_totalQualityDecayRegions"
]

available_report_cols = [c for c in report_cols if c in kpi.columns]
report_kpi = kpi[available_report_cols]

report_kpi_path = TABLES_DIR / "selected_kpi_report_table.csv"
report_kpi.to_csv(report_kpi_path, index=False)

print("\nKPI comparison:")
print(report_kpi)

print("\nSaved:")
print(kpi_path)
print(report_kpi_path)