from pathlib import Path
import pandas as pd
import pm4py

CLEAN_CSV = Path("data/processed/Exp10Run1_clean.csv")

FIGURES_DIR = Path("outputs/figures")
TABLES_DIR = Path("outputs/tables")

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

if not CLEAN_CSV.exists():
    raise FileNotFoundError(f"Cleaned CSV not found: {CLEAN_CSV}")

print("Loading cleaned log...")
df = pd.read_csv(CLEAN_CSV)

# Make sure timestamp is datetime
df["time:timestamp"] = pd.to_datetime(df["time:timestamp"], errors="coerce")
df = df[df["time:timestamp"].notna()]

# Sort log
df = df.sort_values(["case:concept:name", "time:timestamp"])

print("Loaded cleaned log.")
print("Shape:", df.shape)

# Basic event log statistics
num_cases = df["case:concept:name"].nunique()
num_events = len(df)
num_activities = df["concept:name"].nunique()

# Variant analysis using pandas
case_variants = (
    df.groupby("case:concept:name")["concept:name"]
    .apply(lambda x: " -> ".join(x))
    .reset_index(name="variant")
)

variant_counts = (
    case_variants["variant"]
    .value_counts()
    .reset_index()
)

variant_counts.columns = ["variant", "cases"]
variant_counts["share"] = variant_counts["cases"] / num_cases

num_variants = len(variant_counts)

# Save overview table
overview = pd.DataFrame([
    {
        "experiment": 10,
        "run": 1,
        "cases": num_cases,
        "events": num_events,
        "activities": num_activities,
        "variants": num_variants
    }
])

overview_path = TABLES_DIR / "Exp10Run1_log_overview.csv"
variants_path = TABLES_DIR / "Exp10Run1_variants.csv"

overview.to_csv(overview_path, index=False)
variant_counts.head(20).to_csv(variants_path, index=False)

print("\nLog overview:")
print(overview)

print("\nTop 5 variants:")
print(variant_counts.head(5))

print("\nSaved overview table to:", overview_path)
print("Saved variants table to:", variants_path)

# Format dataframe for PM4Py
log = pm4py.format_dataframe(
    df,
    case_id="case:concept:name",
    activity_key="concept:name",
    timestamp_key="time:timestamp"
)

# Discover Directly-Follows Graph
print("\nDiscovering Directly-Follows Graph...")
dfg, start_activities, end_activities = pm4py.discover_dfg(log)

dfg_path = FIGURES_DIR / "Exp10Run1_dfg.png"
pm4py.save_vis_dfg(dfg, start_activities, end_activities, str(dfg_path))

print("Saved Directly-Follows Graph to:", dfg_path)

# Discover Petri net using Inductive Miner
print("\nDiscovering Inductive Miner Petri net...")
net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log)

petri_path = FIGURES_DIR / "Exp10Run1_inductive_miner.png"
pm4py.save_vis_petri_net(net, initial_marking, final_marking, str(petri_path))

print("Saved Inductive Miner model to:", petri_path)

print("\nDiscovery step completed successfully.")