from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

TABLES_DIR = Path("outputs/tables")
FIGURES_DIR = Path("outputs/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

kpi_path = TABLES_DIR / "selected_kpi_report_table.csv"
disposal_path = TABLES_DIR / "selected_disposal_by_experiment.csv"

if not kpi_path.exists():
    raise FileNotFoundError(f"Missing KPI table: {kpi_path}")

if not disposal_path.exists():
    raise FileNotFoundError(f"Missing disposal table: {disposal_path}")

kpi = pd.read_csv(kpi_path)
disposal = pd.read_csv(disposal_path)

# Short experiment labels
kpi["experiment_label"] = "Exp. " + kpi["experiment"].astype(str)
disposal["experiment_label"] = "Exp. " + disposal["experiment"].astype(str)

# 1. Total waiting time
plt.figure(figsize=(6, 4))
plt.bar(kpi["experiment_label"], kpi["mean_totalWaitingTimeRegions"])
plt.xlabel("Experiment")
plt.ylabel("Mean total waiting time")
plt.title("Mean Total Waiting Time by Experiment")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "total_waiting_time_by_experiment.png", dpi=300)
plt.close()

# 2. Cycle time
plt.figure(figsize=(6, 4))
plt.bar(kpi["experiment_label"], kpi["mean_totalTimeInSystemInSeconds"])
plt.xlabel("Experiment")
plt.ylabel("Mean cycle time")
plt.title("Mean Cycle Time by Experiment")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "cycle_time_by_experiment.png", dpi=300)
plt.close()

# 3. Disposal rate
plt.figure(figsize=(6, 4))
plt.bar(disposal["experiment_label"], disposal["disposal_rate"] * 100)
plt.xlabel("Experiment")
plt.ylabel("Disposal rate (%)")
plt.title("Product Disposal Rate by Experiment")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "disposal_rate_by_experiment.png", dpi=300)
plt.close()

print("Generated figures:")
print(FIGURES_DIR / "total_waiting_time_by_experiment.png")
print(FIGURES_DIR / "cycle_time_by_experiment.png")
print(FIGURES_DIR / "disposal_rate_by_experiment.png")