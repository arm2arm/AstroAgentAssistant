# ADQL examples

Use this file to keep validated gaia.aip.de query patterns.

Starter pattern for a reproducible ADQL workflow:

```sql
SELECT TOP 100
    source_id,
    ra,
    dec,
    parallax,
    phot_g_mean_mag
FROM some_table
WHERE parallax IS NOT NULL
```

Recommended operating pattern:
- always name the target table explicitly;
- keep `TOP N` in exploratory queries;
- record the exact query text in notes or workflow outputs;
- state any assumptions about units, epochs, and joins.

To be enriched later with validated gaia.aip.de table-specific examples.
