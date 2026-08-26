# AgentBench API Reference

## Controller Endpoints

The AgentBench controller runs on `localhost:5020` (HTTP + gRPC).

### HTTP API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/get_sessions` | GET | List active sessions |
| `/api/start_task` | POST | Start a new evaluation task |
| `/api/get_task/<task_id>` | GET | Get task status/results |

### gRPC API

Controller listens on port `5020` for gRPC connections.

## Task Worker API

Each task worker exposes:
- `GET /api/get_sessions` - List sessions for this task
- `POST /api/submit` - Submit agent response
- `GET /api/result/<session_id>` - Get evaluation result

## Sample Task Structure (dbbench)

```json
{
  "description": "What are the Notes when the Method is decision?",
  "label": ["Women +60kg Bronze"],
  "create": {
    "database": "wikisql",
    "init": "wikisql_init.sql"
  },
  "table": {
    "table_name": "Jiu-Jitsu Championships Results",
    "table_info": {
      "columns": [
        {"name": "Result", "type": "TEXT"},
        {"name": "Opponent", "type": "TEXT"},
        {"name": "Method", "type": "TEXT"},
        {"name": "Event", "type": "TEXT"},
        {"name": "Notes", "type": "TEXT"}
      ],
      "rows": [...]
    }
  },
  "sql": {
    "query": "SELECT Notes FROM \"Jiu-Jitsu Championships Results\" WHERE Method = 'Decision';",
    "length": 78
  }
}
```

## Function Calling Tools (dbbench)

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "execute_sql",
        "description": "Executes a given SQL statement on the database and returns the result.",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "The SQL query to be executed."
            }
          },
          "required": ["query"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "commit_final_answer",
        "description": "Commits the final answer after all operations are completed.",
        "parameters": {
          "type": "object",
          "properties": {
            "answers": {
              "type": "array",
              "items": {"type": "string"},
              "description": "The list of final answers to commit."
            }
          },
          "required": ["answers"]
        }
      }
    }
  ]
}
```

## Evaluation Metrics

- **Accuracy**: % of tasks with correct final answer
- **SQL Correctness**: % of generated SQL queries that match ground truth
- **Turn Efficiency**: Average turns to complete task
- **Tool Usage**: Correctness of function calling

## Integration Pattern

1. Start task worker: `docker compose up -d dbbench-std`
2. Query controller for available tasks
3. For each task:
   - Parse schema and question
   - Generate SQL via function calling
   - Submit via `commit_final_answer`
   - Collect result
4. Aggregate metrics across all tasks
