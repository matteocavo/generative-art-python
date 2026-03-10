"""
Yantra Engine
Multi-level interlaced triangles with central lotus
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle

# ====== SETTINGS ======
SEED = 101
BG, INK = "black", "white"
DPI, FIGSIZE = 280, (8, 8)

R0 = 1.0
LEVELS = 6          # complexity (higher = more interlacing)
RINGS = 7           # guide circles
LW_MAIN = 1.15
LW_FINE = 0.55
A_MAIN = 0.85
A_FINE = 0.25

rng = np.random.default_rng(SEED)

def polar_pts(r, n, phase=0.0):
    t = np.linspace(0, 2*np.pi, n, endpoint=False) + phase
    return np.column_stack([r*np.cos(t), r*np.sin(t)])

def tri_from_ring(r, phase, upward=True):
    # triangle on circle r: rotate phase, alternate up/down
    base = polar_pts(r, 3, phase)
    if upward:
        return base
    # invert (equivalent 60° rotation for the “down” effect)
    return polar_pts(r, 3, phase + np.pi/3)

fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_aspect("equal")
ax.axis("off")

# Guide circles
ring_r = np.linspace(R0*0.8, R0*4.8, RINGS)
for rr in ring_r:
    ax.add_patch(Circle((0,0), rr, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE))

# Multi-level interlaced triangles
segs = []
tri_r = np.linspace(R0*1.0, R0*4.2, LEVELS)
for i, rr in enumerate(tri_r):
    phase = rng.uniform(0, 2*np.pi)
    up = (i % 2 == 0)
    T = tri_from_ring(rr, phase, upward=up)

    # triangle edges
    for j in range(3):
        segs.append([T[j], T[(j+1)%3]])

    # inner “chords”: connect vertices to next-level triangle (interlacing)
    if i < LEVELS-1:
        rr2 = tri_r[i+1]
        T2 = tri_from_ring(rr2, phase + (np.pi/6 if up else -np.pi/6), upward=not up)
        for j in range(3):
            segs.append([T[j], T2[(j+1)%3]])
            segs.append([T[j], T2[(j+2)%3]])

# Add a central “lotus” (6 petals made of chords)
center_r = R0*0.95
P = polar_pts(center_r, 6, phase=rng.uniform(0, 2*np.pi))
for i in range(6):
    segs.append([P[i], P[(i+2)%6]])
    segs.append([P[i], P[(i+3)%6]])

ax.add_collection(LineCollection(segs, colors=[INK], linewidths=LW_MAIN, alpha=A_MAIN))

# Minimal central sigil
ax.add_patch(Circle((0,0), R0*0.22, fill=False, edgecolor=INK, lw=LW_MAIN, alpha=A_MAIN))

extent = R0*5.2
ax.set_xlim(-extent, extent); ax.set_ylim(-extent, extent)
plt.tight_layout(pad=0)
fig.savefig(OUT_DIR / "08_yantra_engine.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

