#!/usr/bin/env python3
"""
Query a Dask scheduler and print a compact JSON summary.

Usage:
  python3 query_dask_scheduler.py --scheduler tcp://host:8786

This script is designed to be copied to a remote host and run; it avoids
complex quoting and prints a small summary that's easy to read back in.
"""
import argparse
import json

parser = argparse.ArgumentParser(description='Query Dask scheduler')
parser.add_argument('--scheduler', required=True, help='scheduler address e.g. tcp://host:8786')
args = parser.parse_args()

from dask.distributed import Client
c = Client(args.scheduler)
info = c.scheduler_info()
ws = info.get('workers', {})
summary = {'scheduler': info.get('address'), 'n_workers': len(ws), 'workers': {}}
for w,m in ws.items():
    summary['workers'][w] = {
        'nthreads': m.get('nthreads'),
        'memory_limit_bytes': m.get('memory_limit'),
        'memory_limit_GB': round(m.get('memory_limit',0)/(1024**3),3) if m.get('memory_limit') else None,
        'host': m.get('host'),
        'status': m.get('status', None)
    }
try:
    summary['versions'] = c.get_versions()
except Exception as e:
    summary['versions'] = {'error': str(e)}
try:
    summary['ncores'] = c.ncores()
except Exception:
    summary['ncores'] = None

print(json.dumps(summary, indent=2))
