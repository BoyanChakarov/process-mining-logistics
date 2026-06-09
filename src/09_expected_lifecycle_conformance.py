from pathlib import Path
import pandas as pd

CLEAN_LOG = Path("data/processed/selected_experiments_clean.csv")
TABLES_DIR = Path("outputs/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_SEQUENCE = [
    "arrivalAtSource",
    "productCallsForTransportRegion1",
    "assignedToVehicleRegion1",
    "pickedUpRegion1",
    "droppedOffRegion2",
    "startProcessingRegion2",
    "finishedProcessingRegion2",
    "productCallsForTransportRegion3",
    "assignedToVehicleRegion3",
    "pickedUpRegion3",
    "droppedOffRegion3"
]

EXPECTED_START = EXPECTED_SEQUENCE[0]
EXPECTED_END = EXPECTED_SEQUENCE[-1]

if not CLEAN_LOG.exists():
    raise FileNotFoundError(f"Missing cleaned log: {CLEAN_LOG}")

df = pd.read_csv(CLEAN_LOG)
df["time:timestamp"] = pd.to_datetime(df["time:timestamp"], errors="coerce")
df = df[df["time:timestamp"].notna()]
df = df.sort_values(["experiment_id", "case:concept:name", "time:timestamp"])

case_sequences = (
    df.groupby(["experiment_id", "case:concept:name"])["concept:name"]
    .apply(list)
    .reset_index(name="sequence")
)

def classify_sequence(seq):
    if seq == EXPECTED_SEQUENCE:
        return "exact_expected_lifecycle"

    starts_correctly = len(seq) > 0 and seq[0] == EXPECTED_START
    ends_correctly = len(seq) > 0 and seq[-1] == EXPECTED_END

    if starts_correctly and ends_correctly:
        return "complete_but_not_exact"

    if not starts_correctly and ends_correctly:
        return "starts_late"

    if starts_correctly and not ends_correctly:
        return "ends_early"

    return "other_deviation"

case_sequences["classification"] = case_sequences["sequence"].apply(classify_sequence)

summary = (
    case_sequences
    .groupby(["experiment_id", "classification"])
    .size()
    .reset_index(name="cases")
)

total_cases = (
    case_sequences
    .groupby("experiment_id")
    .size()
    .reset_index(name="total_cases")
)

summary = summary.merge(total_cases, on="experiment_id", how="left")
summary["share"] = summary["cases"] / summary["total_cases"]

summary_path = TABLES_DIR / "expected_lifecycle_conformance.csv"
summary.to_csv(summary_path, index=False)

# Report-ready pivot table
pivot = summary.pivot_table(
    index="experiment_id",
    columns="classification",
    values="share",
    fill_value=0
).reset_index()

pivot_path = TABLES_DIR / "expected_lifecycle_conformance_pivot.csv"
pivot.to_csv(pivot_path, index=False)

# Save top non-conforming variants
case_sequences["variant"] = case_sequences["sequence"].apply(lambda x: " -> ".join(x))
non_conforming = case_sequences[
    case_sequences["classification"] != "exact_expected_lifecycle"
]

top_deviations = (
    non_conforming
    .groupby(["experiment_id", "classification", "variant"])
    .size()
    .reset_index(name="cases")
    .sort_values(["experiment_id", "cases"], ascending=[True, False])
)

top_deviation_path = TABLES_DIR / "top_lifecycle_deviations.csv"
top_deviations.to_csv(top_deviation_path, index=False)

print("\nExpected lifecycle conformance:")
print(summary)

print("\nPivot table:")
print(pivot)

print("\nSaved:")
print(summary_path)
print(pivot_path)
print(top_deviation_path)