"""
Square Temple
Mandala with concentric square frames and diagonal gates
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import LineCollection

SEED = 31
KEY = "AUMAaz::0101::breath+sound"
BG, INK = "black", "white"
DPI, FIGSIZE = 260, (8, 8)

R0 = 1.0
RINGS = 6
PETALS = 18
GRID_RINGS = 3

LW_MAIN, LW_FINE = 1.12, 0.52
A_MAIN, A_FINE = 0.82, 0.26

def hash_to_rng(key: str):
    h = 2166136261
    for c in key.encode("utf-8"):
        h ^= c; h = (h * 16777619) & 0xffffffff
    return np.random.default_rng(h)

krng = hash_to_rng(KEY)

def polar_points(r, n, phase=0.0):
    t = np.linspace(0, 2*np.pi, n, endpoint=False) + phase
    return np.column_stack([r*np.cos(t), r*np.sin(t)])

def star_polygon(n, k):
    idx = np.arange(n)
    return np.column_stack([idx, (idx + k) % n])

def axial_to_xy(q, r, radius):
    x = radius * (3/2) * q
    y = radius * (np.sqrt(3) * (r + q/2))
    return x, y

def hex_points(rings):
    pts = []
    for q in range(-rings, rings + 1):
        for r in range(-rings, rings + 1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) <= rings:
                pts.append((q, r))
    return pts

fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_aspect("equal")
ax.axis("off")

# 1) Flower (less dense, more “air”)
HEX_RADIUS = R0 / np.sqrt(3)
centers = []
for q, r in hex_points(GRID_RINGS):
    centers.append(axial_to_xy(q, r, HEX_RADIUS))
centers = np.array(centers) - np.mean(centers, axis=0)

mask = krng.random(len(centers)) > 0.18
for (x, y), keep in zip(centers, mask):
    if keep:
        ax.add_patch(Circle((x, y), R0, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE))

outer_r = (np.max(np.sqrt((centers**2).sum(axis=1))) + R0) * 1.02
ax.add_patch(Circle((0, 0), outer_r, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE))

# 2) Rosette sharp
star_ns = [PETALS, PETALS+8, PETALS+16]
star_ks = [int(krng.integers(3, 6)), int(krng.integers(5, 9)), int(krng.integers(7, 12))]
radii = np.linspace(R0*1.3, R0*3.8, len(star_ns))

for rr, n, k in zip(radii, star_ns, star_ks):
    pts = polar_points(rr, n, phase=krng.uniform(0, 2*np.pi))
    edges = star_polygon(n, k)
    segs = [[pts[i], pts[j]] for i, j in edges]
    ax.add_collection(LineCollection(segs, colors=[INK], linewidths=LW_MAIN*0.85, alpha=A_MAIN*0.55))

# 3) Square temple frames (new)
sq_r = R0 * 4.3
frames = []
for scale, a in [(1.00, 0.32), (0.86, 0.22), (0.72, 0.18)]:
    s = sq_r * scale
    P = np.array([[-s, -s], [s, -s], [s, s], [-s, s], [-s, -s]])
    frames.append((P, a))

for P, a in frames:
    ax.plot(P[:,0], P[:,1], color=INK, lw=LW_MAIN, alpha=a)

# diagonals + “gates”
gate = sq_r * 0.62
ax.plot([-sq_r, sq_r], [-sq_r, sq_r], color=INK, lw=LW_FINE, alpha=A_FINE)
ax.plot([-sq_r, sq_r], [sq_r, -sq_r], color=INK, lw=LW_FINE, alpha=A_FINE)
ax.plot([-gate, gate], [0, 0], color=INK, lw=LW_MAIN, alpha=A_MAIN*0.55)
ax.plot([0, 0], [-gate, gate], color=INK, lw=LW_MAIN, alpha=A_MAIN*0.55)

# 4) Chord network (more “disciplined”)
RINGS2 = RINGS
ring_radii = np.linspace(R0*1.0, R0*4.2, RINGS2)
ring_counts = (np.linspace(12, 36, RINGS2)).astype(int)

all_nodes, offsets, start = [], [], 0
for i, (rr, n) in enumerate(zip(ring_radii, ring_counts)):
    phase = (i*np.pi/(2*RINGS2))
    pts = polar_points(rr, n, phase=phase)
    all_nodes.append(pts)
    offsets.append((start, start+n))
    start += n
all_nodes = np.vstack(all_nodes)

intervals = krng.choice([4, 6, 8, 10, 12], size=3, replace=False)
segs = []
for (a, b) in offsets:
    n = b-a
    step = int(krng.choice(intervals))
    for i in range(n):
        segs.append([all_nodes[a+i], all_nodes[a+(i+step)%n]])

ax.add_collection(LineCollection(segs, colors=[INK], linewidths=LW_FINE, alpha=A_FINE*0.95))

# 5) Sigil “square-ish”
sig_n = int(np.clip(len(KEY), 12, 36))
sig_r = R0*0.78
sig_pts = polar_points(sig_r, sig_n, phase=krng.uniform(0, 2*np.pi))

bytes_key = np.frombuffer(KEY.encode("utf-8"), dtype=np.uint8)
jump = int(np.clip(bytes_key.mean()/7, 2, 11))
path = [0]
used = {0}
for t in range(sig_n-1):
    nxt = (path[-1] + jump + int(bytes_key[t % len(bytes_key)] % 5)) % sig_n
    if nxt in used:
        nxt = (nxt + 3) % sig_n
    path.append(nxt); used.add(nxt)

sig_segs = [[sig_pts[path[i]], sig_pts[path[i+1]]] for i in range(len(path)-1)]
ax.add_collection(LineCollection(sig_segs, colors=[INK], linewidths=LW_MAIN*1.15, alpha=A_MAIN))
ax.add_patch(Circle((0,0), R0*0.22, fill=False, edgecolor=INK, lw=LW_MAIN, alpha=A_MAIN))

extent = R0 * 5.0
ax.set_xlim(-extent, extent)
ax.set_ylim(-extent, extent)
plt.tight_layout(pad=0)
fig.savefig(OUT_DIR / "08_square_temple.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

