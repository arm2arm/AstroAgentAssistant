# AgentBench Full Suite Runner

Master script for running all 10 AgentBench task categories sequentially.

## Usage

```bash
python /tmp/agentbench_full_suite_runner.py
```

## Tasks Covered

1. **dbbench-std** (SQL) - 300 samples
2. **os-std** (Linux) - 144 samples
3. **webshop-std** (E-commerce) - 100 samples
4. **mind2web-std** (Web Navigation) - 100 samples
5. **kg-std** (Knowledge Graph) - 100 samples
6. **alfworld-std** (Text Adventure) - 134 samples
7. **avalon-std** (Card Game) - 50 samples
8. **ltp-std** (Lateral Puzzles EN) - 50 samples
9. **ltp_zh-std** (Lateral Puzzles ZH) - 50 samples
10. **card_game-std** (Card Games) - 50 samples

**Total:** ~1000 samples

## Expected Time

- **dbbench + os_interaction:** ~3 minutes (3.1s/sample for SQL, 7.0s/sample for Linux)
- **Full suite:** 2-3 hours (depending on task availability and Docker setup)

## Output Files

- `/tmp/agentbench_{task_name}_results.json` - Individual task results
- `/tmp/agentbench_master_summary.json` - Complete summary with all tasks
- `/tmp/agentbench_{task_name}_progress.json` - Real-time progress updates

## Known Issues

- **webshop-std:** Requires ~16GB RAM, may timeout on startup
- **mind2web-std, kg-std, avalon-std, ltp-std, ltp_zh-std, card_game-std:** Docker services may not be available (not built by default)
- **alfworld-std:** May fail with "No samples available" due to data path issues
- **os-std:** Docker SDK bug in aiodocker (use `scripts/os_direct_runner.py` instead)

## Script Structure

```python
#!/usr/bin/env python3
"""
Run ALL AgentBench benchmarks with aip-best model.
Tests all 10 task categories.
"""
import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime

# API Configuration
API_URL = "http://141.33.165.84:8000/v1/chat/completions"
MODEL_NAME = "aip-best"
API_KEY = "EMPTY"
CONTROLLER_URL = "http://localhost:5020/api"

# Task configurations
TASKS = {
    "dbbench-std": {
        "name": "DBBench (SQL)",
        "samples": 300,
        "docker_service": "dbbench-std"
    },
    "os-std": {
        "name": "OS Interaction (Linux)",
        "samples": 144,
        "docker_service": "os_interaction-std"
    },
    # ... (all 10 tasks)
}

def call_api(messages, tools=None):
    """Call external API with error handling."""
    # Implementation handles:
    # - reasoning vs content field
    # - tool_calls format
    # - timeout handling
    pass

def start_docker_service(service_name):
    """Start Docker Compose service with timeout."""
    # Implementation handles:
    # - Service startup timeout
    # - Error logging
    # - Wait for readiness
    pass

def run_benchmark(task_key, task_config, num_samples=None):
    """Run full benchmark for one task."""
    # Implementation:
    # - Starts Docker service
    # - Gets available indices
    # - Runs samples with API calls
    # - Saves progress + results
    # - Returns summary
    pass

def main():
    """Main entry point."""
    # Iterates through all tasks
    # Handles skipped tasks gracefully
    # Creates master summary
    # Cleans up Docker containers
    pass

if __name__ == "__main__":
    main()
```

## Customization

### Change Model/API

Edit the configuration section:

```python
API_URL = "http://YOUR_HOST:8000/v1/chat/completions"
MODEL_NAME = "your-model-name"
API_KEY = "your-api-key"
```

### Run Subset of Tasks

Modify the TASKS dictionary to include only desired tasks:

```python
TASKS = {
    "dbbench-std": {...},
    "os-std": {...},
    # Skip other tasks
}
```

### Adjust Sample Count

Pass `num_samples` parameter to `run_benchmark()`:

```python
result = run_benchmark(task_key, task_config, num_samples=50)  # Run 50 samples
```

## Results Interpretation

### Success Criteria

- **status: "OK"** - Model generated response with tool call
- **status: "EMPTY"** - Model returned empty response
- **status: "ERROR"** - API or infrastructure error

### Common Error Patterns

- `start_sample failed` - Controller API error
- `No messages` - Task worker not returning prompts
- `Docker timeout` - Service startup failure
- `No samples available` - Data path issue

### Performance Metrics

- **per_sample_time:** Average seconds per sample
- **success_rate:** Percentage of OK responses
- **total_time:** Total benchmark duration

## Troubleshooting

**Docker service not found:** Some tasks require manual Docker image builds. Check `extra/docker-compose.yml` for available services.

**API timeout:** Increase timeout in `call_api()` or use a faster model.

**Low success rate:** Check if model is using tool calls. Tune system prompt to encourage tool usage.

**Memory issues:** Run tasks sequentially with Docker cleanup between tasks.

## Related Scripts

- `scripts/agentbench_fast_runner.py` - Single-round SQL benchmark
- `scripts/os_direct_runner.py` - Direct OS benchmark (bypasses Docker bug)
- `scripts/plot_agentbench_results.py` - Generate visualization plots
