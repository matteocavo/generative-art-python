"""
Metatron's Cube
Metatron's Cube with complete connections between all 13 points
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

def circle(ax, c, R, lw=1.0, alpha=1.0):
    t = np.linspace(0, 2*np.pi, 800)
    ax.plot(c[0] + R*np.cos(t), c[1] + R*np.sin(t), lw=lw, alpha=alpha)

def metatron(ax, R=1.0, lw=0.9, alpha=0.9, outer=True):
    # 1 center + 6 points on the circle (seed of life) + 6 outer (optional)
    ang = np.linspace(0, 2*np.pi, 6, endpoint=False)
    center = np.array([0.0, 0.0])
    ring1 = np.c_[R*np.cos(ang), R*np.sin(ang)]          # 6
    ring2 = np.c_[2*R*np.cos(ang), 2*R*np.sin(ang)]      # 6 (outer)
    pts = np.vstack([center, ring1, ring2])

    # seed circles (optional but nice)
    circle(ax, center, R, lw=lw, alpha=alpha*0.8)
    for p in ring1:
        circle(ax, p, R, lw=lw*0.85, alpha=alpha*0.6)

    # complete connections between all points
    for i, j in combinations(range(len(pts)), 2):
        ax.plot([pts[i,0], pts[j,0]], [pts[i,1], pts[j,1]],
                lw=lw*0.6, alpha=alpha*0.35)

    if outer:
        circle(ax, center, 2*R, lw=lw*1.2, alpha=alpha)

fig, ax = plt.subplots(figsize=(8, 8), dpi=240)
ax.set_aspect("equal"); ax.axis("off")
fig.patch.set_facecolor("black"); ax.set_facecolor("black")

metatron(ax, R=1.0, lw=1.0, alpha=0.95, outer=True)

ax.relim(); ax.autoscale_view()
fig.savefig(OUT_DIR / "06_metatron_cube.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

