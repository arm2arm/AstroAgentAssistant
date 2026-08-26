# Run plot fallback notes

If scp fails due to permission or quoting issues, use these fallbacks in order:
1. Re-run with scp -o BatchMode=yes -o StrictHostKeyChecking=accept-new
2. Use base64-encode/decode pipeline:
   cat localfile | base64 | ssh host "base64 -d > remotefile"
3. Use ssh heredoc with single-quoted marker: ssh host 'cat > file <<'"'PY'"' ... PY'
