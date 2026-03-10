"""
Organic Stems
Clusters of vertical lines and nodes on a warm paper background
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

W, H = 1400, 900
rng = np.random.default_rng(10)

fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
ax.set_xlim(0, W); ax.set_ylim(0, H)
ax.axis("off")

# slightly warm paper
fig.patch.set_facecolor("#f4f0e8")
ax.set_facecolor("#f4f0e8")

y_axis = H * 0.52
ax.plot([80, W-80], [y_axis, y_axis], lw=1.2, color="black")

def add_cluster(cx, spread_x, n=180):
    for _ in range(n):
        # distribution: more points near the cluster center
        x = rng.normal(cx, spread_x)
        x = np.clip(x, 90, W-90)

        # vertical position and lengths
        y0 = rng.normal(y_axis, H*0.08)
        stem = abs(rng.normal(H*0.12, H*0.10))
        direction = rng.choice([-1, 1])
        y1 = y0 + direction * stem

        # thin lines
        lw = rng.choice([0.35, 0.5, 0.7], p=[0.55, 0.35, 0.10])
        ax.plot([x, x], [y0, y1], lw=lw, color="black", alpha=rng.uniform(0.55, 1.0))

        # “nodes” (filled or empty circles)
        if rng.random() < 0.55:
            r = rng.uniform(2.0, 8.0)
            filled = rng.random() < 0.55
            c = Circle((x, y1), r, facecolor=("black" if filled else "none"),
                       edgecolor="black", lw=0.8)
            ax.add_patch(c)

        # “digital” micro rectangles
        if rng.random() < 0.18:
            w = rng.uniform(6, 22); h = rng.uniform(4, 14)
            rx = x + rng.uniform(-18, 18)
            ry = y0 + rng.uniform(-25, 25)
            ax.add_patch(Rectangle((rx, ry), w, h, facecolor="black",
                                   edgecolor="black", lw=0))

# left and right clusters + a few scattered points
add_cluster(cx=W*0.28, spread_x=W*0.06, n=260)
add_cluster(cx=W*0.78, spread_x=W*0.05, n=220)

# rarer central “bridges”
add_cluster(cx=W*0.50, spread_x=W*0.12, n=70)

plt.tight_layout(pad=0)
fig.savefig(OUT_DIR / "01_organic_stems.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()