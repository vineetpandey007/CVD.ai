# Error Analysis & Model Calibration

- **Expected Calibration Error (ECE):** 0.0045

### Error Rates by Token Length Buckets

- `<100` tokens (n=244): Error Rate = 41.80%
- `100-300` tokens (n=709): Error Rate = 36.53%
- `300-512` tokens (n=433): Error Rate = 37.41%
- `>512` tokens (n=1341): Error Rate = 38.63%

### Reliability Table (10 Bins)

| bin        |   count |   confidence |   accuracy |
|:-----------|--------:|-------------:|-----------:|
| [0.0, 0.1) |       0 |     0        |   0        |
| [0.1, 0.2) |       0 |     0        |   0        |
| [0.2, 0.3) |       1 |     0.299428 |   0        |
| [0.3, 0.4) |    1123 |     0.369113 |   0.370436 |
| [0.4, 0.5) |    1169 |     0.43699  |   0.439692 |
| [0.5, 0.6) |     203 |     0.540988 |   0.55665  |
| [0.6, 0.7) |      46 |     0.6447   |   0.673913 |
| [0.7, 0.8) |      14 |     0.74367  |   0.785714 |
| [0.8, 0.9) |      13 |     0.852944 |   0.769231 |
| [0.9, 1.0) |     158 |     0.993217 |   1        |

### Qualitative Observations
- **High Precision, Lower Recall:** Model precision is 74.4%, but recall is 25.8% at threshold 0.5.
- **Length Sensitivity:** Longer code snippets exceeding the 512-token limit suffer truncation, inflating false negatives.
