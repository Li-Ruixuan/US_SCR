# SCR anchor error against room-scan coverage

### v1-short-2XX / eval_train_2XX_run-205+run-211_kabsch

| nearest room-scan pose | frames | anchor error mm (median / p90) |
|---|---|---|
| 0–30 mm | 8 | 26.3 / 29.9 |
| 30–60 mm | 37 | 16.8 / 31.8 |
| 60–100 mm | 32 | 10.6 / 38.6 |
| 100–200 mm | 0 | – |
| > 200 mm | 0 | – |
| **covered (≤ 30 mm and 10°)** | 0 (0 %) | – |
| **not covered** | 77 (100 %) | 14.7 / 34.7 |

### v1-short-2XX / eval_train_2XX_run-205+run-211

| nearest room-scan pose | frames | anchor error mm (median / p90) |
|---|---|---|
| 0–30 mm | 8 | 56.2 / 81.6 |
| 30–60 mm | 37 | 52.6 / 85.9 |
| 60–100 mm | 32 | 31.6 / 53.4 |
| 100–200 mm | 0 | – |
| > 200 mm | 0 | – |
| **covered (≤ 30 mm and 10°)** | 0 (0 %) | – |
| **not covered** | 77 (100 %) | 40.5 / 77.5 |

### aug-short-2XX / eval_train_2XX_run-205+run-211_kabsch

| nearest room-scan pose | frames | anchor error mm (median / p90) |
|---|---|---|
| 0–30 mm | 8 | 37.0 / 46.0 |
| 30–60 mm | 37 | 17.0 / 29.8 |
| 60–100 mm | 32 | 13.3 / 29.2 |
| 100–200 mm | 0 | – |
| > 200 mm | 0 | – |
| **covered (≤ 30 mm and 10°)** | 0 (0 %) | – |
| **not covered** | 77 (100 %) | 17.0 / 36.4 |

### aug-short-2XX / eval_train_2XX_run-205+run-211

| nearest room-scan pose | frames | anchor error mm (median / p90) |
|---|---|---|
| 0–30 mm | 8 | 30.5 / 39.0 |
| 30–60 mm | 37 | 19.0 / 41.6 |
| 60–100 mm | 32 | 25.6 / 58.0 |
| 100–200 mm | 0 | – |
| > 200 mm | 0 | – |
| **covered (≤ 30 mm and 10°)** | 0 (0 %) | – |
| **not covered** | 77 (100 %) | 23.8 / 53.9 |

### all files pooled

| nearest room-scan pose | frames | anchor error mm (median / p90) |
|---|---|---|
| 0–30 mm | 32 | 35.4 / 62.3 |
| 30–60 mm | 148 | 22.4 / 60.0 |
| 60–100 mm | 128 | 20.8 / 52.6 |
| 100–200 mm | 0 | – |
| > 200 mm | 0 | – |
| **covered (≤ 30 mm and 10°)** | 0 (0 %) | – |
| **not covered** | 308 (100 %) | 23.9 / 56.5 |
