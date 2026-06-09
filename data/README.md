# Data instructions

The original raw dataset is not included in this repository because of its size.

To reproduce the analysis, download and extract the dataset locally, then place the folders in:

data/raw/

Expected structure:

data/raw/
├── Input/
├── LogFiles/
├── LogFilesProductWarmupFilter/
├── Output/
├── OutputWarmupFilter/
└── experimentResults.xlsx

The main files used in this project are:
- LogFilesProductWarmupFilter/Exp{experiment}Run{run}.txt
- OutputWarmupFilter/Exp{experiment}Run{run}.txt
- OutputWarmupFilter/DisposedProducts{experiment}Run{run}.txt

The selected experiments are 10, 14, and 23, using runs 1 to 20.