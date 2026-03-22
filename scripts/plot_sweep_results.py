"""Plot apparent safety vs true safety vs usefulness for sweep results, averaged over seeds."""

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa

SWEEP_DIR = Path("results/sweep_benign_agents/mon_claude-haiku-4-5-20251001__adv_claude-sonnet-4-6__ben_claude-sonnet-4-6/n5")

# Load all seed results
all_metrics = []
for seed_dir in sorted(SWEEP_DIR.glob("seed_*")):
    result_file = seed_dir / "result.json"
    if result_file.exists():
        with open(result_file) as f:
            data = json.load(f)
        all_metrics.append(data["metrics"])
        print(f"Loaded {seed_dir.name}")

n_seeds = len(all_metrics)
n_rounds = len(all_metrics[0])
rounds = list(range(n_rounds))

# Average across seeds
apparent = np.array([[m[r]["apparent_safety"] for r in range(n_rounds)] for m in all_metrics])
true_s = np.array([[m[r]["true_safety"] for r in range(n_rounds)] for m in all_metrics])
useful = np.array([[m[r]["usefulness"] for r in range(n_rounds)] for m in all_metrics])

app_mean, app_std = apparent.mean(axis=0), apparent.std(axis=0)
true_mean, true_std = true_s.mean(axis=0), true_s.std(axis=0)
use_mean = useful.mean(axis=0)

# Plot (matching simulation.py style)
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(rounds, app_mean, "o-", label="Apparent Safety", color="#e63946", linewidth=2)
ax.fill_between(rounds, app_mean - app_std, app_mean + app_std, color="#e63946", alpha=0.15)
ax.plot(rounds, true_mean, "s--", label="True Safety", color="#f4a261", linewidth=2)
ax.fill_between(rounds, true_mean - true_std, true_mean + true_std, color="#f4a261", alpha=0.15)
ax.plot(rounds, use_mean, "^:", label="Usefulness", color="#457b9d", linewidth=2)

ax.set_xlabel("Round")
ax.set_ylabel("Fraction")
ax.set_title(f"Haiku 4.5 Monitor vs Sonnet 4.6 Adversary ({n_seeds} seeds)")
ax.set_ylim(-0.05, 1.1)
ax.set_xticks(rounds)
ax.legend()
ax.grid(True, alpha=0.3)

# Annotate the gap
gap = app_mean[-1] - true_mean[-1]
if gap > 0.05:
    ax.annotate(
        f"capture gap\n= {gap:.2f}",
        xy=(rounds[-1], (app_mean[-1] + true_mean[-1]) / 2),
        xytext=(rounds[-1] - 1.5, 0.5),
        arrowprops=dict(arrowstyle="->", color="gray"),
        fontsize=9, color="gray",
    )

plt.tight_layout()
out_path = SWEEP_DIR.parent.parent / "haiku_monitor_results.png"
plt.savefig(out_path, dpi=150)
print(f"\nPlot saved to {out_path}")
