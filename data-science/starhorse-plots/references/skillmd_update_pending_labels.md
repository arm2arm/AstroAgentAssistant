# SKILL.md update pending — pointer (2026-08-14)

The read-before-write guard blocked patching SKILL.md this turn (dedup
suppressor returns "unchanged" with no content). The following section was
written for SKILL.md and should be merged into it (suggested placement: right
before "# Adding a comparison plot: SHBoost 3-panel pattern"):

---

# Axis labels: always carry the plotted column names (user rule, 2026-08-14)

User mandate: "fix axis names so we recognize what columns are plotting."
EVERY plot's x/y label appends the actual column on a second line:
`r"Distance $d$ [kpc]\n(col: dist50)"`. Raw parquet col → its name; derived
col → derived name (`(col: bprp0)`, `(col: RGal)`, `(col: plx_frac_err)`);
P11/P12 label the unit-converted aliases (`r_med_geo_bj21_kpc`). Baked into
`_sh21_helper`, `_shboost_helper`, `_uncert_helper`; one-line edits elsewhere
(all 39 done 2026-08-14). **Keep BOTH P11 and P12** — different BJ21
estimators (geoRMS vs photo-geometric), they diverge for poor-parallax stars.
Full convention + rationale: references/column_label_convention.md.

---
