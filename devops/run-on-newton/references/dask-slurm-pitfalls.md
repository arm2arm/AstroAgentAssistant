# Dask SLURM pitfalls

- When running Dask LocalCluster under SLURM, set multiprocessing start method to 'fork' (mp.set_start_method('fork')) and guard main with if __name__ == '__main__' to avoid nanny/startup errors.
- Probe parquet schema with pyarrow on one file before passing projections to dask.read_parquet to avoid KeyError when partitions differ.
- Force s3fs endpoint_url in storage_options client_kwargs when running inside batch contexts that lack proper S3 config.
