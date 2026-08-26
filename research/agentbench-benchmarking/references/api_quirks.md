# API Quirks and Workarounds for AgentBench FC

## Key API Behavior Changes

### 1. `start_sample` Returns Prompt Directly

**Expected** (old docs):
```json
{
  "session_id": "abc-123",
  "output": {
    "status": "RUNNING",
    "history": [...]
  }
}
```

**Actual** (current API):
```json
{
  "messages": [...],
  "tools": [...]
}
```

**Workaround**: Use the sample `index` as `session_id` for subsequent `/interact` calls.

### 2. Session ID Handling

The controller doesn't return a session_id. The pattern is:

```python
# Start sample
resp = requests.post(
    "http://localhost:5020/api/start_sample",
    json={"name": "task-name", "index": 0}
)
data = resp.json()  # Contains messages, tools

# Use index as session_id
session_id = 0  # NOT data.get("session_id")

# Interact
requests.post(
    "http://localhost:5020/api/interact",
    json={
        "session_id": session_id,
        "agent_response": {"content": "...", "status": "CONTINUE"}
    }
)
```

### 3. SQL Execution in dbbench

**Don't** call `/execute_sql` separately. The worker:
1. Parses SQL from code blocks in agent responses
2. Executes it internally
3. Returns results in the next history update

**Correct flow**:
```python
# Agent generates:
# ```sql
# SELECT * FROM table WHERE condition
# ```

# Worker executes automatically and returns:
# {
#   "output": {
#     "status": "RUNNING",
#     "history": [...new messages with SQL results...]
#   }
# }
```

### 4. Config Import Paths

Assignment configs use relative imports that resolve from the config file's directory:

```yaml
# WRONG (relative to assignments/):
definition:
  import: tasks/task_assembly.yaml  # Fails!

# CORRECT:
definition:
  import: ../tasks/task_assembly.yaml  # Relative to assignments/

# OR use absolute path:
definition:
  import: /tmp/AgentBench/configs/tasks/task_assembly.yaml
```

### 5. Agent Configuration

The `agent` definition requires specific fields:

```yaml
definition:
  agent:
    import: /path/to/agent_config.yaml
    parameters:
      module: src.client.agents.http_agent.HTTPAgent  # Required
      parameters:
        url: http://localhost:11434/api/chat
        body:
          model: qwen3.6:latest
          stream: false
        prompter:
          name: role_content_dict
          args:
            message_key: messages
            role_key: role
            content_key: content
```

### 6. Tool Call Format

AgentBench expects tool calls in OpenAI-compatible format:

```json
{
  "message": {
    "content": "Explanation...",
    "tool_calls": [
      {
        "function": {
          "name": "bash_action",
          "arguments": {"script": "ls -la"}
        }
      }
    ]
  }
}
```

Ollama Qwen models support this natively when `tools` parameter is provided.

## Task-Specific Notes

### dbbench-std
- SQL in code blocks executed automatically
- Use `commit_final_answer` tool for final answer
- 300 samples, ~43s per sample with 36B model

### os-std
- Uses `bash_action` for commands
- Uses `finish_action` or `answer_action` to complete
- 144 samples

### knowledgegraph-std
- Requires Freebase database
- Download from https://github.com/dki-lab/Freebase-Setup
- Place at `./virtuoso_db/virtuoso.db`

### webshop-std
- Requires ~16GB RAM
- Skip if limited resources

### alfworld-std
- Known memory leak in worker
- Restart after ~50 samples
- Docker build may fail (visdom dependency issue)

## Error Messages and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `invalid session id` | Using wrong session_id format | Use sample index as session_id |
| `File not found` in config | Relative import path issue | Use absolute paths or correct relative paths |
| `Not Found` on interact | Worker not running or session expired | Check `docker ps`, restart worker |
| `visdom` build fails | ALFWorld dependency issue | Skip alfworld-std task |
| `context limit` | Response too long | Increase `max_tokens` in agent config |

## Testing the API

Quick test to verify controller is working:

```bash
# List workers
curl http://localhost:5020/api/list_workers | jq

# Get indices
curl "http://localhost:5020/api/get_indices?name=os-std" | jq '.[0:5]'

# Start sample
curl -X POST http://localhost:5020/api/start_sample \
  -H "Content-Type: application/json" \
  -d '{"name": "os-std", "index": 0}' | jq
```

## References

- Main repo: https://github.com/THUDM/AgentBench
- Paper: https://arxiv.org/abs/2308.03688
- Leaderboard: https://docs.google.com/spreadsheets/d/e/2PACX-1vRR3Wl7wsCgHpwUw1_eUXW_fptAPLL3FkhnW_rua0O1Ji_GIVrpTjY5LaKAhwO-WeARjnY_KNw0SYNJ/pubhtml
