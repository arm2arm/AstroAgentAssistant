#!/usr/bin/env python3
"""Quick single-sample test for Helmholtz Blablador endpoint."""
import requests
import json

API_URL = "https://api.helmholtz-blablador.fz-juelich.de/v1/chat/completions"
API_KEY = "glpat-<YOUR_TOKEN>"

def test_model(model_name, prompt="SELECT 1"):
    """Test a single model with a simple query."""
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a SQL expert. Generate ONLY the SQL query in a ```sql code block. No explanations."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 256
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        msg = data.get("choices", [{}])[0].get("message", {})
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning") or ""
        
        # Check output format
        has_content = bool(content)
        has_reasoning = bool(reasoning)
        
        # Extract SQL
        sql = None
        for text in [content, reasoning]:
            if "```sql" in text:
                sql = text.split("```sql")[1].split("```")[0].strip()
                break
            elif "```" in text:
                sql = text.split("```")[1].split("```")[0].strip()
                break
        
        print(f"Model: {model_name}")
        print(f"  Status: ✅ Success")
        print(f"  Content field: {has_content}")
        print(f"  Reasoning field: {has_reasoning}")
        print(f"  SQL extracted: {sql is not None}")
        if sql:
            print(f"  SQL: {sql[:100]}")
        print()
        
        return {
            "model": model_name,
            "success": True,
            "has_content": has_content,
            "has_reasoning": has_reasoning,
            "sql_extracted": sql is not None,
            "sql": sql
        }
        
    except requests.exceptions.HTTPError as e:
        print(f"Model: {model_name}")
        print(f"  Status: ❌ HTTP Error {e.response.status_code}")
        print(f"  Response: {e.response.text[:200]}")
        print()
        return {"model": model_name, "success": False, "error": str(e)}
    except Exception as e:
        print(f"Model: {model_name}")
        print(f"  Status: ❌ Error: {e}")
        print()
        return {"model": model_name, "success": False, "error": str(e)}

if __name__ == "__main__":
    models = [
        "alias-apertus",
        "alias-large",
        "alias-qwen36-35b",
        "alias-glm-huge",
        "alias-huge"
    ]
    
    print("Testing Helmholtz Blablador models with single sample...\n")
    results = []
    for model in models:
        result = test_model(model)
        results.append(result)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for r in results:
        status = "✅" if r["success"] else "❌"
        sql_status = "SQL" if r.get("sql_extracted") else "No SQL"
        content_status = "content" if r.get("has_content") else "reasoning"
        print(f"{status} {r['model']}: {sql_status} ({content_status})")
