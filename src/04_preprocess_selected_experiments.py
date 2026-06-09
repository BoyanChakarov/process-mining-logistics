from pathlib import Path
import re
import pandas as pd
from tqdm import tqdm

RAW_DIR = Path("data/raw/LogFilesProductWarmupFilter")
OUT_DIR = Path("data/processed")
TABLES_DIR = Path("outputs/tables")

OUT_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Selected experiments for the project comparison
SELECTED_EXPERIMENTS = [10, 14, 23]
RUNS = range(1, 21)

EXPECTED_START = "arrivalAtSource"
EXPECTED_END = "droppedOffRegion3"

all_logs = []

def load_one_file(path: Path, experiment_id: int, run_id: int) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = [c.strip() for c in df.columns]

    required = ["productIDStr", "event", "timeStamp"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")

    # Remove invalid product cases
    df = df[df["productIDStr"].notna()]
    df = df[df["productIDStr"].astype(str).str.strip() != ""]
    df = df[df["productIDStr"].astype(str).str.strip() != "(?)"]

    # Remove missing event/timestamp
    df = df[df["event"].notna()]
    df = df[df["timeStamp"].notna()]

    # Add IDs
    df["experiment_id"] = experiment_id
    df["run_id"] = run_id

    # Convert timestamp
    time_numeric = pd.to_numeric(df["timeStamp"], errors="coerce")
    if time_numeric.notna().mean() > 0.9:
        df["time:timestamp"] = pd.Timestamp("2020-01-01") + pd.to_timedelta(time_numeric, unit="s")
    else:
        df["time:timestamp"] = pd.to_datetime(df["timeStamp"], errors="coerce")

    df = df[df["time:timestamp"].notna()]

    # PM4Py standard names
    # Include experiment/run in case ID so same product IDs across runs do not merge
    df["case:concept:name"] = (
        "Exp" + df["experiment_id"].astype(str)
        + "_Run" + df["run_id"].astype(str)
        + "_" + df["productIDStr"].astype(str)
    )

    df["concept:name"] = df["event"].astype(str)

    if "vehicle" in df.columns:
        df["org:resource"] = df["vehicle"].astype(str)
    elif "vehicleType" in df.columns:
        df["org:resource"] = df["vehicleType"].astype(str)
    else:
        df["org:resource"] = "NA"

    return df


print("Loading selected experiment logs...")

for exp in SELECTED_EXPERIMENTS:
    for run in RUNS:
        path = RAW_DIR / f"Exp{exp}Run{run}.txt"

        if not path.exists():
            print(f"Missing file, skipped: {path}")
            continue

        try:
            df_one = load_one_file(path, exp, run)
            all_logs.append(df_one)
        except Exception as e:
            print(f"Failed to load {path}: {e}")

if not all_logs:
    raise RuntimeError("No logs loaded. Check file paths.")

df = pd.concat(all_logs, ignore_index=True)
df = df.sort_values(["experiment_id", "run_id", "case:concept:name", "time:timestamp"])

# Save full selected event log
selected_path = OUT_DIR / "selected_experiments_clean.csv"
df.to_csv(selected_path, index=False)

print("Saved selected clean log to:", selected_path)
print("Total shape:", df.shape)

# Create run-level overview
overview_rows = []

for (exp, run), group in df.groupby(["experiment_id", "run_id"]):
    num_cases = group["case:concept:name"].nunique()
    num_events = len(group)
    num_activities = group["concept:name"].nunique()

    case_variants = (
        group.groupby("case:concept:name")["concept:name"]
        .apply(lambda x: " -> ".join(x))
    )

    overview_rows.append({
        "experiment": exp,
        "run": run,
        "cases": num_cases,
        "events": num_events,
        "activities": num_activities,
        "variants": case_variants.nunique()
    })

overview_by_run = pd.DataFrame(overview_rows)
overview_by_run.to_csv(TABLES_DIR / "selected_overview_by_run.csv", index=False)

# Create experiment-level overview
exp_rows = []

for exp, group in df.groupby("experiment_id"):
    num_cases = group["case:concept:name"].nunique()
    num_events = len(group)
    num_activities = group["concept:name"].nunique()

    case_variants = (
        group.groupby("case:concept:name")["concept:name"]
        .apply(lambda x: " -> ".join(x))
    )

    main_variant_cases = case_variants.value_counts().iloc[0]
    main_variant_share = main_variant_cases / num_cases

    # Complete cases: first event is arrivalAtSource and last event is droppedOffRegion3
    case_start_end = group.groupby("case:concept:name")["concept:name"].agg(["first", "last"])
    complete_cases = case_start_end[
        (case_start_end["first"] == EXPECTED_START)
        & (case_start_end["last"] == EXPECTED_END)
    ]

    exp_rows.append({
        "experiment": exp,
        "runs": group["run_id"].nunique(),
        "cases": num_cases,
        "events": num_events,
        "activities": num_activities,
        "variants": case_variants.nunique(),
        "main_variant_cases": main_variant_cases,
        "main_variant_share": main_variant_share,
        "complete_cases": len(complete_cases),
        "complete_case_share": len(complete_cases) / num_cases
    })

overview_by_experiment = pd.DataFrame(exp_rows)
overview_by_experiment.to_csv(TABLES_DIR / "selected_overview_by_experiment.csv", index=False)

print("\nOverview by experiment:")
print(overview_by_experiment)

print("\nSaved:")
print(TABLES_DIR / "selected_overview_by_run.csv")
print(TABLES_DIR / "selected_overview_by_experiment.csv")