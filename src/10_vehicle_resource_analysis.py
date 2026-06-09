from pathlib import Path
import pandas as pd
import re

INPUT_TABLE = Path("outputs/tables/selected_output_combined.csv")
TABLES_DIR = Path("outputs/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

if not INPUT_TABLE.exists():
    raise FileNotFoundError(
        f"Missing {INPUT_TABLE}. Run src/05_kpi_comparison_selected.py first."
    )

df = pd.read_csv(INPUT_TABLE)

def clean_vehicle_type(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    invalid_values = ["", "NA", "nan", "None", "ERROR DATA TYPE!", "(?)"]

    if value in invalid_values:
        return None

    # Expected examples: UAV:2, HDF:1, AGV:4
    match = re.match(r"([A-Za-z]+)", value)

    if match:
        return match.group(1)

    return None

# Use recommended vehicle columns from output data
vehicle_columns = {
    "Region 1": {
        "vehicle_col": "vehiclePickedUpRegion1",
        "waiting_col": "waitingTimeRegion1",
        "travel_col": "travelTimeRegion1"
    },
    "Region 3": {
        "vehicle_col": "vehiclePickedUpRegion3",
        "waiting_col": "waitingTimeRegion3",
        "travel_col": "travelTimeRegion3"
    }
}

rows = []

for region, cols in vehicle_columns.items():
    vehicle_col = cols["vehicle_col"]
    waiting_col = cols["waiting_col"]
    travel_col = cols["travel_col"]

    if vehicle_col not in df.columns:
        print(f"Missing vehicle column: {vehicle_col}")
        continue

    temp = df.copy()
    temp["region"] = region
    temp["vehicle_type_clean"] = temp[vehicle_col].apply(clean_vehicle_type)

    temp = temp[temp["vehicle_type_clean"].notna()]

    for col in [waiting_col, travel_col]:
        if col in temp.columns:
            temp[col] = pd.to_numeric(temp[col], errors="coerce")

    grouped = (
        temp
        .groupby(["experiment_id", "region", "vehicle_type_clean"])
        .agg(
            products=("productIDString", "count") if "productIDString" in temp.columns else (vehicle_col, "count"),
            mean_waiting_time=(waiting_col, "mean"),
            mean_travel_time=(travel_col, "mean")
        )
        .reset_index()
    )

    rows.append(grouped)

if not rows:
    raise RuntimeError("No vehicle/resource data could be analyzed.")

resource_table = pd.concat(rows, ignore_index=True)

# Add share within experiment and region
resource_table["total_region_products"] = (
    resource_table
    .groupby(["experiment_id", "region"])["products"]
    .transform("sum")
)

resource_table["share"] = (
    resource_table["products"] / resource_table["total_region_products"]
)

resource_table = resource_table.sort_values(
    ["experiment_id", "region", "products"],
    ascending=[True, True, False]
)

resource_path = TABLES_DIR / "vehicle_resource_analysis.csv"
resource_table.to_csv(resource_path, index=False)

# Compact report version
report_table = resource_table.copy()
report_table["share_percent"] = report_table["share"] * 100

report_table = report_table[
    [
        "experiment_id",
        "region",
        "vehicle_type_clean",
        "products",
        "share_percent",
        "mean_waiting_time",
        "mean_travel_time"
    ]
]

report_path = TABLES_DIR / "vehicle_resource_report_table.csv"
report_table.to_csv(report_path, index=False)

print("\nVehicle/resource analysis:")
print(report_table)

print("\nSaved:")
print(resource_path)
print(report_path)