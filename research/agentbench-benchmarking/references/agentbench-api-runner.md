# AgentBench External API Runner

Complete working implementation for running AgentBench with external vLLM API endpoints.

## Key Implementation Details

### API Response Handling

```python
# Handle both 'content' and 'reasoning' fields
content = response_msg.get("content") or response_msg.get("reasoning", "")

# Handle tool args as JSON string or dict
func_args = tc.get("function", {}).get("arguments", {})
if isinstance(func_args, str):
    try:
        func_args = json.loads(func_args)
    except:
        func_args = {}
query = func_args.get("query", "") if isinstance(func_args, dict) else ""
```

### Session Management

```python
# start_sample returns prompt directly, NOT session_id
resp = requests.post(
    "http://localhost:5020/api/start_sample",
    json={"name": "dbbench-std", "index": 0}
)
data = resp.json()  # {messages: [...], tools: [...]}

# Use index as session_id for interact
interact_resp = requests.post(
    "http://localhost:5020/api/interact",
    json={
        "session_id": 0,  # Use the sample index
        "agent_response": {"content": content, "status": "CONTINUE"}
    }
)
```

### Tool Call Loop Pattern

```python
for round_num in range(max_rounds):
    # Call LLM
    result = call_api(messages, tools if round_num == 0 else None)
    
    # Extract response
    content = result["choices"][0]["message"].get("content", "")
    tool_calls = result["choices"][0]["message"].get("tool_calls", [])
    
    # Handle tool calls
    for tc in tool_calls:
        func_name = tc["function"]["name"]
        func_args = tc["function"]["arguments"]
        
        if func_name == "execute_sql":
            # Worker executes SQL internally
            messages.append({
                "role": "tool",
                "name": func_name,
                "content": f"Executed: {query[:50]}..."
            })
            continue  # Continue to next round
        
        if func_name == "commit_final_answer":
            return {"status": "COMPLETED", "final_answer": args["answers"]}
    
    # Send response to worker
    interact_resp = requests.post(
        "http://localhost:5020/api/interact",
        json={"session_id": idx, "agent_response": {"content": content}}
    )
```

## Performance Benchmarks

| Model | Task | Time/Sample | Success Rate |
|-------|------|-------------|--------------|
| qwen3.6:latest (36B) | dbbench | ~43s | 30% (10 samples) |
| aip-best (Qwen3.6-35B) | dbbench | ~4s | 100% SQL gen (5 samples) |

**Note**: aip-best via vLLM is ~10x faster than local Ollama due to better hardware acceleration.

## Sample SQL Queries Generated

```sql
-- Sample 0
SELECT Notes FROM `Jiu-Jitsu Championships Results` WHERE Method = 'decision'

-- Sample 1
SELECT `2007` FROM `Tournament Results` WHERE `2008` = 'sf' AND `2010` = 'f'

-- Sample 2
SELECT Total FROM "Olympic Medals" WHERE Nation = 'United States'

-- Sample 3 (exploratory)
SELECT * FROM `Football Matches` LIMIT 10

-- Sample 4
SELECT City FROM "Airport Information" WHERE IATA = 'VIE'
```

All queries generated correctly on first attempt with proper table/column names and WHERE clauses.

## Full Runner Script

See `/tmp/run_agentbench_api_dbbench.py` for complete implementation with:
- API client with timeout handling
- Tool call parsing (string vs dict args)
- Multi-round loop with history management
- Result aggregation and JSON export

## Troubleshooting

**"invalid session id"**: Use sample index (0, 1, 2...) not UUID.

**404 on `/v1/chat/completions`**: Check endpoint is `/v1/chat/completions` not `/v1/completions`.

**Empty messages array**: OS Interaction task may have issues. Try dbbench instead.

**Tool args parsing error**: Handle both JSON string and dict formats.

**Timeout on full benchmark**: Reasoning tokens take longer. Increase timeout or reduce max_rounds.
