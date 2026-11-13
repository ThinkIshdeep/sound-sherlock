# Experiments and reproduction

Run `python scripts/evaluate_all.py` from this repository. The report is written to `reports/evaluation-results.json`. This executes real calculations; model quality is separate from test success.

## Recorded baseline

```json
{
  "detector": "spectral_energy_baseline",
  "auroc": 1.0,
  "average_precision": 0.9999999999999998,
  "false_positive_rate": 0.3111111111111111,
  "recall": 1.0,
  "isolation_forest": {
    "auroc": 0.7135802469135802,
    "false_positive_rate": 0.03333333333333333,
    "recall": 0.06666666666666667
  },
  "test_recordings": 180,
  "threshold": 0.0275065585965067,
  "note": "Synthetic held-out recordings with changed noise. The default spectral baseline is compared with Isolation Forest, not hidden behind it. No real-device validation is bundled."
}
```

## Interpretation

Synthetic audio reference, spectral baseline and Isolation Forest. No real-device fault diagnosis or DCASE benchmark.

The raw reports describe whether measurements are synthetic benchmarks, controlled regression fixtures or invariants. Do not interpret regression-fixture accuracy as a held-out real-world score. Preserve seeds and splits when comparing changes.
