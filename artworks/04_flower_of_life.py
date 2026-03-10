"""
Flower of Life
Sacred geometry: overlapping hexagonal circles
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt

def flower_of_life(ax, R=1.0, rings=4, lw=0.8, alpha=0.9):
    # hexagonal coordinates -> plane
    def hex_to_xy(q, r):
        x = R * (np.sqrt(3) * q + np.sqrt(3)/2 * r)
        y = R * (3/2 * r)
        return x, y

    centers = []
    for q in range(-rings, rings+1):
        for r in range(-rings, rings+1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) <= rings:
                centers.append(hex_to_xy(q, r))

    t = np.linspace(0, 2*np.pi, 600)
    for (cx, cy) in centers:
        x = cx + R*np.cos(t)
        y = cy + R*np.sin(t)
        ax.plot(x, y, lw=lw, alpha=alpha)

fig, ax = plt.subplots(figsize=(8, 8), dpi=220)
ax.set_aspect("equal"); ax.axis("off")
fig.patch.set_facecolor("black"); ax.set_facecolor("black")

flower_of_life(ax, R=1.0, rings=5, lw=0.8, alpha=0.85)

# auto limits
ax.relim(); ax.autoscale_view()
fig.savefig(OUT_DIR / "04_flower_of_life.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

