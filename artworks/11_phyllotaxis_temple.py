"""
Phyllotaxis Temple
Golden spiral with constellation chord network and square gate
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle

SEED = 303
BG, INK = "black", "white"
DPI, FIGSIZE = 280, (8, 8)

R0 = 1.0
N = 1200                 # punti spirale (densità)
SPIRAL_MAX = R0*4.7
RINGS = 7
CHORDS = 2200            # rete costellazione
LW_MAIN = 1.10
LW_FINE = 0.48
A_MAIN = 0.80
A_FINE = 0.20

rng = np.random.default_rng(SEED)

fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_aspect("equal")
ax.axis("off")

# Guide circles
for rr in np.linspace(R0*1.0, R0*4.9, RINGS):
    ax.add_patch(Circle((0,0), rr, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE))

# Phyllotaxis (golden spiral)
phi = (1 + 5**0.5) / 2
golden_angle = 2*np.pi*(1 - 1/phi)

i = np.arange(N)
r = SPIRAL_MAX * np.sqrt(i / (N-1))
theta = i * golden_angle
x = r*np.cos(theta)
y = r*np.sin(theta)
pts = np.column_stack([x, y])

# Points as “nodes” (micro-circles)
# (comment this loop for a lighter render)
for k in range(0, N, 6):
    rr = 0.012*R0 + 0.02*R0*(r[k]/SPIRAL_MAX)
    ax.add_patch(Circle((pts[k,0], pts[k,1]), rr, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE*1.1))

# Temple gates: quadrato + diagonali (squaring the circle)
S = R0*4.55
sq = np.array([[-S,-S],[S,-S],[S,S],[-S,S],[-S,-S]])
ax.plot(sq[:,0], sq[:,1], color=INK, lw=LW_MAIN, alpha=A_MAIN*0.35)
ax.plot([-S,S],[-S,S], color=INK, lw=LW_FINE, alpha=A_FINE)
ax.plot([-S,S],[S,-S], color=INK, lw=LW_FINE, alpha=A_FINE)

# Constellation chords: connect points “close” in r but far in angle
# -> organic but readable network
segs = []
idx = rng.integers(0, N, size=CHORDS)
for a in idx:
    # scegli b con r simile ma theta diverso
    target_r = r[a] + rng.normal(0, SPIRAL_MAX*0.03)
    b = int(np.clip(np.searchsorted(r, target_r), 0, N-1))
    # “ritual” angular offset
    b = (b + int(rng.integers(20, 140))) % N
    segs.append([pts[a], pts[b]])

ax.add_collection(LineCollection(segs, colors=[INK], linewidths=LW_FINE, alpha=A_FINE*0.85))

# Central sigil
ax.add_patch(Circle((0,0), R0*0.24, fill=False, edgecolor=INK, lw=LW_MAIN, alpha=A_MAIN))
ax.add_patch(Circle((0,0), R0*0.55, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE))

extent = R0*5.2
ax.set_xlim(-extent, extent); ax.set_ylim(-extent, extent)
plt.tight_layout(pad=0)
fig.savefig(OUT_DIR / "11_phyllotaxis_temple.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

