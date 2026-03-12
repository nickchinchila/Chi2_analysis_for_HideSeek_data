# Chi2 Analysis for Hide & Seek Data Library

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic example](#basic-example)
  - [Parameters](#parameters)
  - [Running on a cluster (SLURM)](#running-on-a-cluster-slurm)
  - [Running locally with MPI](#running-locally-with-mpi)
- [Output](#output)
- [Parallelization strategy](#parallelization-strategy)
- [Author](#author)

---

## Overview

This library was developed to perform statistical comparisons between observed and expected TOD from the Hide & Seek data. For each combination of **horn**, **hour** and **frequency bin**, it computes:

- **χ² statistic** (using `scipy.stats.chisquare`)
- **p‑value** (currently computed but not stored)
- **RMSE** (optional)

The analysis is parallelised with **MPI** at two levels:
1. **Between nodes** – horns are distributed among available compute nodes.
2. **Within a node** – hours are distributed among the processes (ranks) running on that node.

Intermediate results are saved in **memory‑mapped files** (`.dat`) to minimise RAM usage and allow efficient parallel writes. After all processes finish, the master process (rank 0) consolidates the data into a single **HDF5 file** and, if requested, generates **waterfall plots** (χ² and/or RMSE per horn).

A job coordinator script (`submission_coordinator.py`) creates a JSON configuration file and launches the MPI job through the (`mpi_worker`) either via SLURM (`sbatch`) or locally (`mpiexec`).

---

## Features

- **Automatic task distribution** – no need to manually split horns/hours.
- **Supports SLURM clusters** – generates submission scripts on the fly.
- **Local execution** – for testing on workstations with `mpiexec`.
- **Configurable analysis** – number of horns, hours, bins, date, paths, and optional parameters.
- **Memory‑mapped I/O** – handles large datasets without loading everything into RAM.
- **Final HDF5 output** – compressed, self‑describing file with all results.
- **Waterfall plots** – visualise χ² and/or RMSE matrices for selected horns.
- **Graceful handling of missing/invalid data** – bins with insufficient samples are marked as `NaN`.

---

## Requirements

- Python ≥ 3.8.2
- `os`
- `sys`
- `random`
- `glob`
- `copy`
- `pathlib`
- `json`
- `subprocess`
- `numpy`
- `scipy`
- `h5py`
- `matplotlib`
- `mpi4py`
- MPICH MPI implementation for parallel execution
- (Optional) SLURM workload manager for cluster submission

---

## Installation

add later
## Usage

### Basic example

Create a script similar to `how_to_use_example.py` where the parameters are:

**Parameters**  
- `n_horns` : int  
  Number of horns to process.  
- `n_hours` : int  
  Number of hours of observation on each horn.  
- `n_bins` : int  
  Number of frequency bins in each TOD.  
- `obs_date` : str  
  Observation date used in filenames (format YYYYMMDD).  
- `base_results_path` : str or Path  
  Root directory where all outputs will be stored.  
- `base_obsTOD_path` : str or Path  
  Directory containing observed TOD files (input).  
- `base_expTOD_path` : str or Path  
  Directory containing expected TOD files (input).  
- `dof` : int, optional  
  Degrees of freedom for chi-square test. If None, uses `(number_data_points - 1)`.  
- `analysis_identifier` : int, optional  
  Number identifier of the current analysis. If not provided, a random ID is used to create a unique output subdirectory.  
- `show_process_info` : bool, optional (Not active)  
  If True, prints debug info per process.  
- `rmse` : bool, optional  
  If True, also compute RMSE alongside chi-square.  
- `min_valid_samples` : int, optional  
  Minimum number of valid (positive) expected data required per bin; otherwise the bin is marked as NaN.  

**File naming convention**  
The library expects TOD files named as:

bingo_tod_horn_<horn><obs_date><hour:02d>0000.h5

inside the respective observation and expectation directories.

### Running on a cluster (SLURM)

Set `slurm=True` in `run_parallel`. The coordinator will:

- Write a JSON config file (`config_job_<id>.json`)
- Generate a SLURM submission script (`submit_job_<id>.sh`)
- Submit it with `sbatch`

Make sure to edit the generated script to load required modules and activate your Python environment (the coordinator adds commented lines as placeholders).

### Running locally with MPI

Set `slurm=False`. The coordinator will execute:

`mpiexec -n <total_num_process> python mpi_worker.py <config_file>`

on the local machine. Ensure mpiexec is in your PATH and your environment is properly configured.

## Output

After a successful run, the following directory structure is created under base_results_path/chi2_4_HS_analysis_<identifier>/:

memmaps/               # temporary .dat files (deleted after consolidation)
waterfalls/            # PNG plots (if plot_waterfalls=True)
results/               # final HDF5 file with all results

## HDF5 structure

- `/chi2/horn_<xxx>` – dataset of shape `(n_hours, n_bins)` containing χ² values.
- `/rmse/horn_<xxx>` – present only if `rmse=True`.

Datasets are compressed with gzip (level 4). Missing/invalid bins are stored as `NaN` (attribute `missing_data_flag` is set to `'NaN'`).

## Waterfall plots

For each plotted horn, a PNG file `waterfall_horn<id>.png` is saved. It shows:

- **Left**: χ² values (log color scale, black for `NaN`)
- **Right**: RMSE values (linear scale) – only if `rmse=True`

## Parallelization strategy

- **Node‑level distribution**  
  Horns are assigned to nodes in round‑robin fashion. All processes on a node share the same list of horns.

- **Process‑level distribution**  
  Within a node, hours are distributed among the local ranks, again round‑robin. Each process thus receives a set of `(horn, hour)` pairs.

- **Work execution**  
  Each process opens the corresponding observed and expected HDF5 files, computes χ² (and RMSE) per frequency bin, and writes the result directly into the memory‑mapped file for that horn.

- **Synchronisation**  
  Barriers are used to ensure that all writes are finished before the master proceeds to consolidation and cleanup.

This design minimises inter‑process communication and file contention, because:

- Each horn is written by multiple processes, but they write to different rows (hours) of the same memmap – this is safe because different rows are independent.
- No two processes write to the same byte of a memmap at the same time.

Author

Nicolli Soares
[11/03/2026]
