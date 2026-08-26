# Fallback Dask cell

# Add this near the top of your notebook so non-interactive runs don't hang when the
# expected external scheduler is unavailable. Adjust addresses/worker counts as needed.

try:
    from dask.distributed import Client, LocalCluster
    import socket
    target = "tcp://141.33.4.144:8786"
    try:
        client = Client(target)
        print(f"Connected to Dask scheduler: {client}")
    except Exception as e:
        print(f"Could not connect to {target}: {e}. Falling back to LocalCluster.")
        cluster = LocalCluster(n_workers=4, threads_per_worker=1)
        client = Client(cluster)
        print(f"Started LocalCluster: {client}")
except Exception as e:
    print("Dask import/start failed:", e)
