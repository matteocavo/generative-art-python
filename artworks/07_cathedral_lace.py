"""
Cathedral Lace
High-density mandala with double rosette pass
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import LineCollection

SEED = 23
KEY = "AUMAaz::0101::breath+sound"
BG, INK = "black", "white"
DPI, FIGSIZE = 260, (8, 8)

R0 = 1.0
RINGS = 7
PETALS = 20
GRID_RINGS = 4

LW_MAIN, LW_FINE = 1.05, 0.50
A_MAIN, A_FINE = 0.82, 0.26

rng = np.random.default_rng(SEED)

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

# 1) Flower-of-life + extra tangency circles (more “lace”)
HEX_RADIUS = R0 / np.sqrt(3)
centers = []
for q, r in hex_points(GRID_RINGS):
    x, y = axial_to_xy(q, r, HEX_RADIUS)
    centers.append((x, y))
centers = np.array(centers) - np.mean(centers, axis=0)

mask = krng.random(len(centers)) > 0.06  # denser
for (x, y), keep in zip(centers, mask):
    if keep:
        ax.add_patch(Circle((x, y), R0, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE))

# smaller tangent circles for detail
for (x, y), keep in zip(centers, mask):
    if keep and krng.random() < 0.35:
        ax.add_patch(Circle((x, y), R0*0.52, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE*0.9))

outer_r = (np.max(np.sqrt((centers**2).sum(axis=1))) + R0) * 1.03
ax.add_patch(Circle((0, 0), outer_r, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE))

# 2) Rosettes multilayer (more layers + “double pass”)
star_layers = 5
base = PETALS
star_ns = [base + 4*i for i in range(star_layers)]
star_ks = [int(krng.integers(2+i, 6+i)) for i in range(star_layers)]
radii = np.linspace(R0*1.1, R0*3.9, star_layers)

for rr, n, k in zip(radii, star_ns, star_ks):
    phase = krng.uniform(0, 2*np.pi)
    pts = polar_points(rr, n, phase=phase)

    # first pass
    edges = star_polygon(n, k)
    segs = [[pts[i], pts[j]] for i, j in edges]
    ax.add_collection(LineCollection(segs, colors=[INK], linewidths=LW_MAIN*0.85, alpha=A_MAIN*0.55))

    # second pass (finer) for “cathedral” effect
    edges2 = star_polygon(n, max(2, k-1))
    segs2 = [[pts[i], pts[j]] for i, j in edges2[::2]]
    ax.add_collection(LineCollection(segs2, colors=[INK], linewidths=LW_FINE, alpha=A_FINE*0.9))

# 3) Denser chord network with rule: density grows outward
ring_radii = np.linspace(R0*0.9, R0*4.4, RINGS)
ring_counts = (np.linspace(12, 42, RINGS)).astype(int)

all_nodes, ring_offsets, start = [], [], 0
for i, (rr, n) in enumerate(zip(ring_radii, ring_counts)):
    phase = (i*np.pi/(2*RINGS)) + krng.uniform(-0.25, 0.25)
    pts = polar_points(rr, n, phase=phase)
    all_nodes.append(pts)
    ring_offsets.append((start, start+n))
    start += n
all_nodes = np.vstack(all_nodes)

intervals = krng.choice([3, 5, 7, 9, 11, 13], size=4, replace=False)

segs = []
for ri, (a, b) in enumerate(ring_offsets):
    n = b - a
    # further out = more connections
    repeats = 1 + ri//2
    for _ in range(repeats):
        step = int(krng.choice(intervals))
        for i in range(n):
            j = (i + step) % n
            segs.append([all_nodes[a+i], all_nodes[a+j]])

# inter-ring links: denser outward
for r in range(RINGS - 1):
    a0, a1 = ring_offsets[r]
    b0, b1 = ring_offsets[r+1]
    na, nb = (a1-a0), (b1-b0)
    links = int(min(na, nb) * (0.25 + 0.08*r))
    for _ in range(links):
        i = int(krng.integers(0, na))
        j = int((i/na)*nb + krng.integers(-3, 4))
        j = int(np.clip(j, 0, nb-1))
        segs.append([all_nodes[a0+i], all_nodes[b0+j]])

ax.add_collection(LineCollection(segs, colors=[INK], linewidths=LW_FINE, alpha=A_FINE))

# 4) Central sigil with extra “ring”
sig_n = int(np.clip(len(KEY) + 6, 14, 44))
sig_r = R0 * 0.82
sig_pts = polar_points(sig_r, sig_n, phase=krng.uniform(0, 2*np.pi))

bytes_key = np.frombuffer(KEY.encode("utf-8"), dtype=np.uint8)
jump = int(np.clip(bytes_key.mean()/6, 2, 13))
path, used = [0], {0}

for t in range(sig_n-1):
    nxt = (path[-1] + jump + int(bytes_key[t % len(bytes_key)] % 7)) % sig_n
    if nxt in used:
        nxt = (nxt + 2) % sig_n
    path.append(nxt); used.add(nxt)

sig_segs = [[sig_pts[path[i]], sig_pts[path[i+1]]] for i in range(len(path)-1)]
ax.add_collection(LineCollection(sig_segs, colors=[INK], linewidths=LW_MAIN*1.2, alpha=A_MAIN))
ax.add_patch(Circle((0, 0), R0*0.23, fill=False, edgecolor=INK, lw=LW_MAIN, alpha=A_MAIN))

extent = R0 * 5.2
ax.set_xlim(-extent, extent)
ax.set_ylim(-extent, extent)
plt.tight_layout(pad=0)
fig.savefig(OUT_DIR / "07_cathedral_lace.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

