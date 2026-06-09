# Process Mining for Quality-Aware Smart-Pallet Logistics

This repository contains the reproducible workflow for the Process Mining group project on quality-aware smart-pallet logistics.

The project analyzes a simulation-generated logistics dataset involving products transported through three regions using UAVs, human-driven forklifts, and automated guided vehicles. The goal is to compare dispatching and fleet configurations using process mining and KPI analysis.

## Research Focus

The project compares three experiment configurations:

- Experiment 10: balanced fleet with random dispatching
- Experiment 14: balanced fleet with quality-aware and shortest-distance dispatching
- Experiment 23: no-UAV fleet with quality-aware and shortest-distance dispatching

The main research objective is to identify which configuration leads to the most stable product lifecycle, lowest waiting time, lowest cycle time, and lowest product disposal.

## Methods

The analysis includes:

- event log preprocessing
- Directly-Follows Graph discovery
- variant analysis
- expected lifecycle conformance analysis
- KPI comparison
- disposal analysis
- vehicle/resource analysis
- report figure generation

## Repository Structure

```text
process-mining-logistics/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── README.md
├── src/
│   ├── 00_check_setup.py
│   ├── 01_load_one_log.py
│   ├── 02_preprocess_one_log.py
│   ├── 03_discovery_one_log.py
│   ├── 04_preprocess_selected_experiments.py
│   ├── 05_kpi_comparison_selected.py
│   ├── 06_disposal_analysis_selected.py
│   ├── 08_discovery_selected_experiments.py
│   ├── 09_expected_lifecycle_conformance.py
│   ├── 10_vehicle_resource_analysis.py
│   └── 11_generate_final_report_figures.py
├── outputs/
│   ├── figures/
│   └── tables/
└── report/
    ├── process_mining_logistics_report.tex
    └── process_mining_logistics_report.pdf
```

## Data

The raw dataset is not included in this repository because of its large size.

To reproduce the analysis, download and extract the original dataset locally and place it in:

```text
data/raw/
```

Expected local data structure:

```text
data/raw/
├── Input/
├── LogFiles/
├── LogFilesProductWarmupFilter/
├── Output/
├── OutputWarmupFilter/
└── experimentResults.xlsx
```

The main files used in this project are:

- `LogFilesProductWarmupFilter/Exp{experiment}Run{run}.txt`
- `OutputWarmupFilter/Exp{experiment}Run{run}.txt`
- `OutputWarmupFilter/DisposedProducts{experiment}Run{run}.txt`

The selected experiments are 10, 14, and 23, using runs 1 to 20.

See `data/README.md` for more details.

## Setup

This project was developed using Python and PM4Py.

Create a virtual environment:

```powershell
py -3.13 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Graphviz must also be installed on the system for PM4Py visualizations.

Check Graphviz:

```powershell
dot -V
```

## Reproduce the Analysis

After placing the raw data in `data/raw/`, run the scripts in this order:

```powershell
python src\02_preprocess_one_log.py
python src\03_discovery_one_log.py
python src\04_preprocess_selected_experiments.py
python src\05_kpi_comparison_selected.py
python src\06_disposal_analysis_selected.py
python src\08_discovery_selected_experiments.py
python src\09_expected_lifecycle_conformance.py
python src\10_vehicle_resource_analysis.py
python src\11_generate_final_report_figures.py
```

## Main Outputs

Important generated tables:

```text
outputs/tables/selected_discovery_summary.csv
outputs/tables/expected_lifecycle_conformance.csv
outputs/tables/expected_lifecycle_conformance_pivot.csv
outputs/tables/selected_kpi_report_table.csv
outputs/tables/selected_disposal_by_experiment.csv
outputs/tables/vehicle_resource_report_table.csv
```

Important generated figures:

```text
outputs/figures/Exp10_all_runs_dfg.png
outputs/figures/Exp14_all_runs_dfg.png
outputs/figures/Exp23_all_runs_dfg.png
outputs/figures/total_waiting_time_by_experiment.png
outputs/figures/cycle_time_by_experiment.png
outputs/figures/disposal_rate_by_experiment.png
```

## Report

The final report is available in:

```text
report/process_mining_logistics_report.pdf
```

The LaTeX source file is available in:

```text
report/process_mining_logistics_report.tex
```

## Summary of Findings

The analysis shows that Experiment 14 is the strongest selected configuration. Compared with the baseline configuration in Experiment 10, it reduces total waiting time and cycle time while maintaining high lifecycle conformance and zero product disposal.

Experiment 23 is not recommended because it has lower lifecycle conformance, higher waiting time, much higher cycle time, and a 4.95% product disposal rate.

## Notes on Large Files

The following files are intentionally not tracked in Git because they are large or reproducible intermediate files:

```text
data/raw/
data/interim/
data/processed/
outputs/xes/
outputs/tables/selected_output_combined.csv
```

These files can be regenerated locally by running the scripts after placing the raw dataset in `data/raw/`.

## Authors

- Boyan Chakarov
- Johan Tunc
- Sem de Jong