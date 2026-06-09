from pathlib import Path
import pandas as pd
import pm4py

CLEAN_LOG = Path("data/processed/selected_experiments_clean.csv")
FIGURES_DIR = Path("outputs/figures")
TABLES_DIR = Path("outputs/tables")

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

if not CLEAN_LOG.exists():
    raise FileNotFoundError(f"Missing cleaned log: {CLEAN_LOG}")

df = pd.read_csv(CLEAN_LOG)
df["time:timestamp"] = pd.to_datetime(df["time:timestamp"], errors="coerce")
df = df[df["time:timestamp"].notna()]
df = df.sort_values(["experiment_id", "case:concept:name", "time:timestamp"])

summary_rows = []

for exp, group in df.groupby("experiment_id"):
    print(f"\nProcessing Experiment {exp}...")

    log = pm4py.format_dataframe(
        group,
        case_id="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp"
    )

    # Directly-Follows Graph
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)

    dfg_path = FIGURES_DIR / f"Exp{exp}_all_runs_dfg.png"
    pm4py.save_vis_dfg(dfg, start_activities, end_activities, str(dfg_path))

    print("Saved DFG:", dfg_path)

    # Variant analysis
    case_variants = (
        group.groupby("case:concept:name")["concept:name"]
        .apply(lambda x: " -> ".join(x))
        .reset_index(name="variant")
    )

    variant_counts = (
        case_variants["variant"]
        .value_counts()
        .reset_index()
    )

    variant_counts.columns = ["variant", "cases"]
    variant_counts["share"] = variant_counts["cases"] / group["case:concept:name"].nunique()

    variant_path = TABLES_DIR / f"Exp{exp}_all_runs_variants.csv"
    variant_counts.head(20).to_csv(variant_path, index=False)

    summary_rows.append({
        "experiment": exp,
        "cases": group["case:concept:name"].nunique(),
        "events": len(group),
        "activities": group["concept:name"].nunique(),
        "variants": len(variant_counts),
        "main_variant_cases": variant_counts.iloc[0]["cases"],
        "main_variant_share": variant_counts.iloc[0]["share"]
    })

summary = pd.DataFrame(summary_rows)
summary_path = TABLES_DIR / "selected_discovery_summary.csv"
summary.to_csv(summary_path, index=False)

print("\nDiscovery summary:")
print(summary)

print("\nSaved discovery summary to:", summary_path)