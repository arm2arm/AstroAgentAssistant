# Approved REANA environments

Approved environment source repository:

```text
https://gitlab-p4n.aip.de/punch_public/reana/environments
```

Current local policy:
- use an environment from the approved repository;
- do not invent custom environments;
- default workflow memory should be `32GB` unless explicitly changed.

Common observed environment images from successful workflows:

- `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro.9845`
- `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c`

Observed workflow schema pattern on the local REANA dev backend:

```yaml
workflow:
  type: serial
  specification:
    steps:
      - name: run-analysis
        environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro.9845
        commands:
          - python analysis.py
        compute_backend: kubernetes
```

Practical note:
- `environment` and `commands` are the important keys used in working examples.
