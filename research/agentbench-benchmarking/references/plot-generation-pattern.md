# AgentBench Benchmark Results Visualization

## Plot Generation Pattern

When visualizing AgentBench benchmark results, generate matplotlib plots with the following structure:

### Required Plots

1. **Summary Bar Chart** (`agentbench_summary_plot.png`)
   - X-axis: Categories (SQL Generated, Failed/Error)
   - Y-axis: Number of samples
   - Colors: Green (#4CAF50) for success, Red (#F44336) for failure
   - Add value labels on bars with percentages
   - Title: "AgentBench DBBench Results\nModel: {model_name} ({N} samples)"
   - Size: 10x6 inches, 150 DPI

2. **Detailed 4-Panel Figure** (`agentbench_results_plot.png`)
   - **Top-left**: Success rate pie chart with explode effect
   - **Top-right**: Response length distribution histogram with mean line
   - **Bottom-left**: Tool call usage bar chart
   - **Bottom-right**: Top 5 sample SQL queries as text table
   - Size: 14x10 inches, 150 DPI

### Code Template

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np

# Load results
with open('/tmp/agentbench_fast_results_{model}.json', 'r') as f:
    data = json.load(f)

results = data['results']
ok_results = [r for r in results if r.get('status') == 'OK' and r.get('sql')]
failed_results = [r for r in results if r.get('error') or r.get('status') == 'UNKNOWN']

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(f'AgentBench DBBench Benchmark Results\nModel: {model}', fontsize=14, fontweight='bold')

# 1. Pie chart
ax1 = axes[0, 0]
sizes = [len(ok_results), len(failed_results)]
labels = ['SQL Generated', 'Failed/Error']
colors = ['#4CAF50', '#F44336']
ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, explode=(0.05, 0))
ax1.set_title('Success Rate', fontweight='bold')

# 2. Histogram
ax2 = axes[0, 1]
if ok_results:
    content_lengths = [r['content_length'] for r in ok_results]
    ax2.hist(content_lengths, bins=10, color='#2196F3', alpha=0.7, edgecolor='black')
    ax2.axvline(np.mean(content_lengths), color='red', linestyle='--', label=f'Mean: {np.mean(content_lengths):.0f} chars')
    ax2.set_xlabel('Response Length (characters)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Response Length Distribution', fontweight='bold')
    ax2.legend()

# 3. Tool call usage
ax3 = axes[1, 0]
if ok_results:
    tool_call_counts = [r.get('tool_calls', 0) for r in ok_results]
    unique, counts = np.unique(tool_call_counts, return_counts=True)
    ax3.bar(unique, counts, color='#FF9800', alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Number of Tool Calls')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Tool Call Usage (Successful Queries)', fontweight='bold')
    ax3.set_xticks(unique)

# 4. Sample queries
ax4 = axes[1, 1]
ax4.axis('off')
if ok_results:
    sorted_results = sorted(ok_results, key=lambda x: x['content_length'], reverse=True)[:5]
    text = "Top 5 Longest Responses:\n\n"
    for i, r in enumerate(sorted_results, 1):
        sql_preview = r['sql'][:60] + "..." if len(r['sql']) > 60 else r['sql']
        text += f"{i}. Sample {r['index']} ({r['content_length']} chars):\n   {sql_preview}\n\n"
    ax4.text(0.1, 0.95, text, transform=ax4.transAxes, fontsize=9, 
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax4.set_title('Sample SQL Queries', fontweight='bold')

plt.tight_layout()
plt.savefig('/tmp/agentbench_results_plot.png', dpi=150, bbox_inches='tight')
```

### Telegram Delivery

Send plots to Telegram using:

```bash
hermes send --to telegram:CHAT_ID "MEDIA:/tmp/agentbench_summary_plot.png"
hermes send --to telegram:CHAT_ID "MEDIA:/tmp/agentbench_results_plot.png"
```

For data files (JSON, CSV), use:

```bash
hermes send --to telegram:CHAT_ID "[[as_document]] /tmp/agentbench_results.json"
```

### Key Metrics to Display

- Total samples
- Success count and percentage
- Failed/error count and percentage
- Average response length
- Average time per sample
- Sample SQL queries (top 5 by length or complexity)

### Output Format

Always save plots as PNG with:
- DPI: 150 or higher
- Bbox: tight
- Background: white (publication-ready)
- Font: sans-serif, bold titles
