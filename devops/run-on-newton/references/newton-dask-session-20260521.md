# Newton Dask run notes (2026-05-21)

Short notes and reproduction steps for running Dask+Datashader jobs on Newton from a Hermes session.

1. Use a single-node SBATCH allocation and run LocalCluster inside it. SBATCH example:

#!/bin/bash
#SBATCH --job-name=shboost_dask
#SBATCH --output=shboost_dask_%j.out
#SBATCH --error=shboost_dask_%j.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G

module load anaconda
source activate myenv
python run_shboost_dask.py

2. Important runtime guards in Python:

- use if __name__ == '__main__':
- set multiprocessing start method to 'fork' (mp.set_start_method('fork'))

3. S3 and pyarrow probe:

- Force storage_options['client_kwargs']['endpoint_url'] to the S3 endpoint (https://s3.data.aip.de:9000) to ensure s3fs works inside batch.
- Probe a single parquet file with pyarrow.parquet.ParquetFile(...) to read the schema before passing columns to dask.read_parquet.

4. Cache intermediate results to a partitioned parquet under the working dir to avoid re-downloading large S3 datasets.

5. Use sbatch --parsable to capture JOBID.

6. Use sbatch --parsable to capture JOBID, and verify outputs with ls -l and sha256sum before uploading to S3.
