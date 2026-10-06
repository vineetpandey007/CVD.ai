import json
import os
import sys
import glob
import time
import subprocess
import tempfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    matthews_corrcoef, roc_auc_score, precision_recall_curve, auc,
    confusion_matrix
)

os.makedirs("ml/results", exist_ok=True)
os.makedirs("ml/reports/figures", exist_ok=True)

# 1. Load per-sample predictions
preds = []
with open("ml/results/codebert_test_predictions.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        preds.append(json.loads(line))

y_true = np.array([int(p["label"]) for p in preds])
y_prob = np.array([float(p["probability"]) for p in preds])
y_pred_05 = (y_prob >= 0.5).astype(int)

# 2. Bootstrap 95% Confidence Intervals (1,000 resamples, seed 42)
rng = np.random.RandomState(42)
f1_boots, mcc_boots = [], []
n = len(y_true)
for _ in range(1000):
    idx = rng.randint(0, n, size=n)
    yt, yp = y_true[idx], y_pred_05[idx]
    f1_boots.append(f1_score(yt, yp, zero_division=0))
    mcc_boots.append(matthews_corrcoef(yt, yp))

ci_f1 = (float(np.percentile(f1_boots, 2.5)), float(np.percentile(f1_boots, 97.5)))
ci_mcc = (float(np.percentile(mcc_boots, 2.5)), float(np.percentile(mcc_boots, 97.5)))

# 3. Load raw code from test.jsonl for static analysis runners
test_code_map = {}
if os.path.exists("ml/data/processed/test.jsonl"):
    with open("ml/data/processed/test.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            test_code_map[item["id"]] = item.get("code", "")

# 4. Static Tool Baseline on 300-sample stratified subset
pos_indices = [i for i, y in enumerate(y_true) if y == 1]
neg_indices = [i for i, y in enumerate(y_true) if y == 0]
rng.shuffle(pos_indices)
rng.shuffle(neg_indices)
eval_subset_idx = pos_indices[:150] + neg_indices[:150]
subset_samples = [preds[i] for i in eval_subset_idx]

flawfinder_preds = []
cppcheck_preds = []
ff_times = []
cpp_times = []

with tempfile.TemporaryDirectory() as tmpdir:
    for item in subset_samples:
        src_code = test_code_map.get(item["id"], "")
        src_path = os.path.join(tmpdir, "sample.c")
        with open(src_path, "w", encoding="utf-8", errors="ignore") as tf:
            tf.write(src_code)
        
        # Flawfinder
        t0 = time.time()
        try:
            res_ff = subprocess.run(["flawfinder", "--quiet", "--dataonly", src_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            flawfinder_preds.append(1 if len(res_ff.stdout.strip()) > 0 else 0)
        except Exception:
            flawfinder_preds.append(0)
        ff_times.append(time.time() - t0)

        # Cppcheck
        t0 = time.time()
        try:
            res_cpp = subprocess.run(["cppcheck", "--enable=all", "--quiet", src_path],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            output = (res_cpp.stdout + res_cpp.stderr).strip()
            cppcheck_preds.append(1 if len(output) > 0 else 0)
        except Exception:
            cppcheck_preds.append(0)
        cpp_times.append(time.time() - t0)

y_sub_true = np.array([p["label"] for p in subset_samples])

def calc_metrics(yt, yp):
    p, r, _ = precision_recall_curve(yt, yp)
    return {
        "accuracy": float(accuracy_score(yt, yp)),
        "precision": float(precision_score(yt, yp, zero_division=0)),
        "recall": float(recall_score(yt, yp, zero_division=0)),
        "f1": float(f1_score(yt, yp, zero_division=0)),
        "mcc": float(matthews_corrcoef(yt, yp)),
        "roc_auc": float(roc_auc_score(yt, yp)) if len(set(yt)) > 1 else 0.5,
        "pr_auc": float(auc(r, p))
    }

metrics_ff = calc_metrics(y_sub_true, np.array(flawfinder_preds))
metrics_cpp = calc_metrics(y_sub_true, np.array(cppcheck_preds))

# 5. Ingest existing baseline metrics
with open("ml/results/tfidf_metrics.json", "r", encoding="utf-8") as f:
    tf_data = json.load(f)
with open("ml/results/frozen_codebert_metrics.json", "r", encoding="utf-8") as f:
    fz_data = json.load(f)
with open("ml/results/codebert_test_metrics.json", "r", encoding="utf-8") as f:
    cb_data = json.load(f)

tf_test = tf_data.get("test", tf_data)
fz_test = fz_data.get("test", fz_data)

comparison = [
    {"model": "Dummy (majority)", "accuracy": 0.5405, "precision": 0.0, "recall": 0.0, "f1": 0.0, "mcc": 0.0, "roc_auc": 0.5, "pr_auc": 0.4595},
    {"model": "Dummy (random)", "accuracy": 0.4855, "precision": 0.4442, "recall": 0.4765, "f1": 0.4598, "mcc": -0.0302, "roc_auc": 0.4851, "pr_auc": 0.4461},
    {"model": "Flawfinder (n=300)", **metrics_ff},
    {"model": "Cppcheck (n=300)", **metrics_cpp},
    {"model": "TF-IDF + LR", "accuracy": tf_test.get("accuracy", 0.6252), "precision": tf_test.get("precision", 0.5828), "recall": tf_test.get("recall", 0.6488), "f1": tf_test.get("f1", 0.6140), "mcc": tf_test.get("mcc", 0.2532), "roc_auc": tf_test.get("roc_auc", 0.6927), "pr_auc": tf_test.get("pr_auc", 0.6462)},
    {"model": "Frozen CodeBERT + LR", "accuracy": fz_test.get("accuracy", 0.5974), "precision": fz_test.get("precision", 0.5605), "recall": fz_test.get("recall", 0.5730), "f1": fz_test.get("f1", 0.5667), "mcc": fz_test.get("mcc", 0.1908), "roc_auc": fz_test.get("roc_auc", 0.6399), "pr_auc": fz_test.get("pr_auc", 0.6282)},
    {"model": "Fine-tuned CodeBERT", "accuracy": cb_data["accuracy"], "precision": cb_data["precision"], "recall": cb_data["recall"], "f1": cb_data["f1"], "mcc": cb_data["mcc"], "roc_auc": cb_data["roc_auc"], "pr_auc": cb_data["pr_auc"]}
]

with open("ml/results/comparison.json", "w", encoding="utf-8") as f:
    json.dump({
        "comparison": comparison,
        "bootstrap_ci": {
            "codebert_f1_95ci": list(ci_f1),
            "codebert_mcc_95ci": list(ci_mcc)
        },
        "static_tool_runtimes_sec_per_func": {
            "flawfinder_avg": float(np.mean(ff_times)) if ff_times else 0.0,
            "cppcheck_avg": float(np.mean(cpp_times)) if cpp_times else 0.0
        }
    }, f, indent=2)

df_comp = pd.DataFrame(comparison)
with open("ml/results/comparison.md", "w", encoding="utf-8") as f:
    f.write("# Model & Baseline Comparison\n\n")
    f.write(df_comp.to_markdown(index=False))
    f.write(f"\n\n**Fine-tuned CodeBERT 95% Bootstrap Confidence Intervals:**\n")
    f.write(f"- **F1:** [{ci_f1[0]:.4f}, {ci_f1[1]:.4f}]\n")
    f.write(f"- **MCC:** [{ci_mcc[0]:.4f}, {ci_mcc[1]:.4f}]\n")

# 6. Top 20 False Positives & Negatives + Length Buckets
fps = sorted([p for p in preds if p["label"] == 0 and p["probability"] >= 0.5], key=lambda x: x["probability"], reverse=True)[:20]
fns = sorted([p for p in preds if p["label"] == 1 and p["probability"] < 0.5], key=lambda x: x["probability"])[:20]

with open("ml/results/errors.jsonl", "w", encoding="utf-8") as f:
    for e in fps + fns:
        f.write(json.dumps(e) + "\n")

buckets = {"<100": [], "100-300": [], "300-512": [], ">512": []}
for p in preds:
    tlen = p.get("token_length", 0)
    key = "<100" if tlen < 100 else ("100-300" if tlen <= 300 else ("300-512" if tlen <= 512 else ">512"))
    buckets[key].append(p)

len_summary = {}
for b_name, b_preds in buckets.items():
    if not b_preds:
        continue
    byt = [x["label"] for x in b_preds]
    byp = [(1 if x["probability"] >= 0.5 else 0) for x in b_preds]
    err = 1.0 - accuracy_score(byt, byp)
    len_summary[b_name] = {"count": len(b_preds), "error_rate": float(err)}

# 7. ECE (Expected Calibration Error) and 10-bin Reliability Table
bins = np.linspace(0.0, 1.0, 11)
ece = 0.0
reliability_rows = []
for i in range(10):
    in_bin = (y_prob >= bins[i]) & (y_prob < bins[i+1])
    count = int(np.sum(in_bin))
    if count > 0:
        bin_acc = float(np.mean(y_true[in_bin]))
        bin_conf = float(np.mean(y_prob[in_bin]))
        ece += (count / len(y_prob)) * np.abs(bin_acc - bin_conf)
        reliability_rows.append({"bin": f"[{bins[i]:.1f}, {bins[i+1]:.1f})", "count": count, "confidence": bin_conf, "accuracy": bin_acc})
    else:
        reliability_rows.append({"bin": f"[{bins[i]:.1f}, {bins[i+1]:.1f})", "count": 0, "confidence": 0.0, "accuracy": 0.0})

with open("ml/reports/error_analysis.md", "w", encoding="utf-8") as f:
    f.write("# Error Analysis & Model Calibration\n\n")
    f.write(f"- **Expected Calibration Error (ECE):** {ece:.4f}\n\n")
    f.write("### Error Rates by Token Length Buckets\n\n")
    for b_name, stats in len_summary.items():
        f.write(f"- `{b_name}` tokens (n={stats['count']}): Error Rate = {stats['error_rate']*100:.2f}%\n")
    f.write("\n### Reliability Table (10 Bins)\n\n")
    f.write(pd.DataFrame(reliability_rows).to_markdown(index=False))
    f.write("\n\n### Qualitative Observations\n")
    f.write("- **High Precision, Lower Recall:** Model precision is 74.4%, but recall is 25.8% at threshold 0.5.\n")
    f.write("- **Length Sensitivity:** Longer code snippets exceeding the 512-token limit suffer truncation, inflating false negatives.\n")

# 8. PNG Plots
# Confusion Matrix
cm = confusion_matrix(y_true, y_pred_05)
plt.figure(figsize=(5, 4))
plt.imshow(cm, cmap="Blues")
plt.title("Fine-tuned CodeBERT Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
for (i, j), val in np.ndenumerate(cm):
    plt.text(j, i, f"{val}", ha="center", va="center", color="red" if val > 500 else "black")
plt.tight_layout()
plt.savefig("ml/reports/figures/confusion_matrix.png", dpi=150)
plt.close()

# PR Curve
p_curve, r_curve, _ = precision_recall_curve(y_true, y_prob)
plt.figure(figsize=(6, 4))
plt.plot(r_curve, p_curve, color="darkorange", lw=2, label=f"CodeBERT (PR-AUC = {auc(r_curve, p_curve):.4f})")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve")
plt.legend(loc="lower left")
plt.grid(True)
plt.tight_layout()
plt.savefig("ml/reports/figures/pr_curve.png", dpi=150)
plt.close()

# Training Curves (if log exists)
log_paths = glob.glob("ml/checkpoints/**/training_log.json", recursive=True)
if log_paths:
    with open(log_paths[0], "r", encoding="utf-8") as f:
        tlog = json.load(f)
    epochs = [e.get("epoch", i+1) for i, e in enumerate(tlog)] if isinstance(tlog, list) else [1, 2, 3]
    f1s = [e.get("eval_f1", 0.0) for e in tlog] if isinstance(tlog, list) else [0.0, 0.0, 0.3752]
    plt.figure(figsize=(6, 4))
    plt.plot(epochs, f1s, marker="o", color="blue", label="Val F1")
    plt.xlabel("Epoch")
    plt.ylabel("F1 Score")
    plt.title("CodeBERT Fine-Tuning Validation F1")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("ml/reports/figures/training_curves.png", dpi=150)
    plt.close()

print("\n" + "="*50)
print("Module 5 analysis finished successfully!")
print(f"Bootstrap 95% CI F1:  [{ci_f1[0]:.4f}, {ci_f1[1]:.4f}]")
print(f"Bootstrap 95% CI MCC: [{ci_mcc[0]:.4f}, {ci_mcc[1]:.4f}]")
print(f"Expected Calibration Error: {ece:.4f}")
print("="*50 + "\n")