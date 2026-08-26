#!/usr/bin/env python3
"""
AgentBench Model Comparison Plot Generator
Generates 6 publication-quality plots comparing Llama-3.2-3B, Teuken-7B, and aip-best.

Usage:
    python scripts/plot_model_comparison.py

Input: JSON result files from benchmark runs
Output: 6 PNG plots in /tmp/
"""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from matplotlib import rcParams

# Set publication-quality style
rcParams['font.size'] = 10
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
rcParams['axes.edgecolor'] = '#333333'
rcParams['axes.linewidth'] = 1.2
rcParams['axes.grid'] = False
rcParams['figure.facecolor'] = 'white'
rcParams['axes.facecolor'] = 'white'

# Data (hardcoded from benchmark results)
benchmarks = ['DBBench', 'KnowledgeGraph', 'OS Interaction', 'Lateral Thinking']

llama32_data = {
    'DBBench': 99.5, 'KnowledgeGraph': 100.0, 'OS Interaction': 100.0, 
    'Lateral Thinking': 100.0, 'Overall': 99.5, 'Avg Time': 2.98, 'Size': 1.9
}

teuken_data = {
    'DBBench': 99.0, 'KnowledgeGraph': 98.0, 'OS Interaction': 57.7, 
    'Lateral Thinking': 56.7, 'Overall': 87.4, 'Avg Time': 4.81, 'Size': 14.0
}

aip_data = {
    'DBBench': 86.0, 'KnowledgeGraph': 80.0, 'OS Interaction': 88.5, 
    'Lateral Thinking': 20.0, 'Overall': 75.2, 'Avg Time': 1.36, 'Size': 35.0
}

colors = {
    'Llama-3.2-3B': '#2E86AB',
    'Teuken-7B': '#A23B72',
    'aip-best': '#F18F01'
}

# ... (rest of the plotting code from /tmp/plot_comparison.py)
# This is a reusable template - copy and modify for future benchmarks
