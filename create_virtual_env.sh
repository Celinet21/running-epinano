#!/bin/bash

### Creates two python virtual environemnts required for running EpiNano.
### Creates within the current working directory.

module load python/3.8.3
python3 -m venv epinano1
source epinano1/bin/activate
python -m pip install "dask[complete]"  
pip install pysam
pip install scikit-learn==0.20.2
deactivate

module switch python/3.8.3 python/3.6.5
python3 -m venv epinano2
source epinano2/bin/activate
python -m pip install "dask[complete]"  
pip install pysam
pip install scikit-learn==0.20.2
deactivate
