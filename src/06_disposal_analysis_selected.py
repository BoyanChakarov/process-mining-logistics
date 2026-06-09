from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("data/raw/OutputWarmupFilter")
TABLES_DIR = Path("outputs/tables")
TABLES_DIR.mkdir(parents=True, exist_ok=True)

SELECTED_EXPERIMENTS = [10, 14, 23]
RUNS = range(1, 21)

disposed_rows = []

def count_disposed_products(path: Path) -> int:
    """
    Counts disposed products in a DisposedProducts file.
    Handles empty files, header-only files, and normal table files.
    """
    if not path.exists():
        return 0

    # If file is completely empty
    if path.stat().st_size == 0:
        return 0

    try:
        df = pd.read_csv(path, sep=None, engine="python")
        df.columns = [c.strip() for c in df.columns]

        # If there is a product identifier column, count unique products
        possible_id_cols = [
            "productIDString",
            "productIDStr",
            "productID",
            "productNr"
        ]

        for col in possible_id_cols:
            if col in df.columns:
                return df[col].dropna().astype(str).nunique()

        # Otherwise count rows
        return len(df)

    except Exception:
        # Fallback: count non-empty lines, assuming first line may be header
        lines = [
            line.strip()
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()
        ]

        if len(lines) <= 1:
            return 0

        return len(lines) - 1


for exp in SELECTED_EXPERIMENTS:
    for run in RUNS:
        path = OUTPUT_DIR / f"DisposedProducts{exp}Run{run}.txt"
        disposed_count = count_disposed_products(path)

        disposed_rows.append({
            "experiment": exp,
            "run": run,
            "disposed_products": disposed_count
        })

disposed_by_run = pd.DataFrame(disposed_rows)
disposed_by_run.to_csv(TABLES_DIR / "selected_disposed_by_run.csv", index=False)

disposed_by_experiment = (
    disposed_by_run
    .groupby("experiment", as_index=False)
    .agg(
        runs=("run", "nunique"),
        disposed_products=("disposed_products", "sum"),
        mean_disposed_per_run=("disposed_products", "mean")
    )
)

# Add processed products from previous KPI table
kpi_path = TABLES_DIR / "selected_kpi_report_table.csv"

if kpi_path.exists():
    kpi = pd.read_csv(kpi_path)
    kpi = kpi[["experiment", "products"]]

    disposed_by_experiment = disposed_by_experiment.merge(
        kpi,
        on="experiment",
        how="left"
    )

    disposed_by_experiment["total_products_including_disposed"] = (
        disposed_by_experiment["products"]
        + disposed_by_experiment["disposed_products"]
    )

    disposed_by_experiment["disposal_rate"] = (
        disposed_by_experiment["disposed_products"]
        / disposed_by_experiment["total_products_including_disposed"]
    )

disposed_by_experiment.to_csv(
    TABLES_DIR / "selected_disposal_by_experiment.csv",
    index=False
)

print("\nDisposed products by experiment:")
print(disposed_by_experiment)

print("\nSaved:")
print(TABLES_DIR / "selected_disposed_by_run.csv")
print(TABLES_DIR / "selected_disposal_by_experiment.csv")