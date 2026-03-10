"""
Cipher Mandala
Mandala with Flower-of-Life, rosettes, chord network and central sigil
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import LineCollection

# =========================
# "ART DIRECTOR" PARAMETERS
# =========================
SEED = 23
KEY = "AUMAaz::0101::breath+sound"   # change this to get a unique sigil

BG = "black"          # "white" for paper look
INK = "white"         # "black" if BG="white"

DPI = 260
FIGSIZE = (8, 8)

# Mandala scale
R0 = 1.0              # unità base
RINGS = 6             # polar rings
PETALS = 18           # "petals" for rosettes
GRID_RINGS = 3        # flower of life density

# Line weights / alpha
LW_MAIN = 1.1
LW_FINE = 0.55
A_MAIN = 0.80
A_FINE = 0.28

rng = np.random.default_rng(SEED)

# ==========
# UTILITIES
# ==========
def hash_to_rng(key: str):
    # deterministic RNG from string (no extra libraries)
    h = 2166136261
    for c in key.encode("utf-8"):
        h ^= c
        h *= 16777619
        h &= 0xffffffff
    return np.random.default_rng(h)

krng = hash_to_rng(KEY)

def polar_points(r, n, phase=0.0):
    t = np.linspace(0, 2*np.pi, n, endpoint=False) + phase
    return np.column_stack([r*np.cos(t), r*np.sin(t)])

def star_polygon(n, k):
    # indices to connect {n/k}
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

# =========================
# FIGURE SETUP
# =========================
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_aspect("equal")
ax.axis("off")

# ==================================
# 1) FLOWER-OF-LIFE (SMART SELECTION)
# ==================================
# center distance ~ R0 for harmonic intersections
HEX_RADIUS = R0 / np.sqrt(3)
centers = []
for q, r in hex_points(GRID_RINGS):
    x, y = axial_to_xy(q, r, HEX_RADIUS)
    centers.append((x, y))
centers = np.array(centers)
centers -= centers.mean(axis=0)

# Non-trivial selection: use KEY to decide which circles to draw
mask = krng.random(len(centers)) > 0.12  # density
for (x, y), keep in zip(centers, mask):
    if keep:
        ax.add_patch(Circle((x, y), R0, fill=False, edgecolor=INK,
                            lw=LW_FINE, alpha=A_FINE))

# outer “aura” circle
outer_r = (np.max(np.sqrt((centers**2).sum(axis=1))) + R0) * 1.02
ax.add_patch(Circle((0, 0), outer_r, fill=False, edgecolor=INK,
                    lw=LW_FINE, alpha=A_FINE*0.9))

# ==================================
# 2) ROSETTES (STAR POLYGONS LAYERED)
# ==================================
# choose {n/k} pattern from KEY
star_ns = [PETALS, PETALS+6, PETALS+12]
star_ks = [
    int(krng.integers(2, 6)),
    int(krng.integers(3, 8)),
    int(krng.integers(4, 10)),
]

rosette_radii = np.linspace(R0*1.2, R0*3.6, len(star_ns))
for rr, n, k in zip(rosette_radii, star_ns, star_ks):
    phase = krng.uniform(0, 2*np.pi)
    pts = polar_points(rr, n, phase=phase)
    edges = star_polygon(n, k)

    segs = [[pts[i], pts[j]] for i, j in edges]
    ax.add_collection(LineCollection(
        segs, colors=[INK], linewidths=LW_MAIN*0.9, alpha=A_MAIN*0.55
    ))

# =========================================
# 3) CHORD NETWORK (CONSTRAINED + MUSICAL)
# =========================================
# Nodes on multiple rings; connections chosen with rules (no chaos)
ring_radii = np.linspace(R0*0.9, R0*4.2, RINGS)
ring_counts = (np.linspace(10, 34, RINGS)).astype(int)

all_nodes = []
ring_offsets = []
start = 0
for i, (rr, n) in enumerate(zip(ring_radii, ring_counts)):
    phase = (i * np.pi / (2*RINGS)) + krng.uniform(-0.2, 0.2)
    pts = polar_points(rr, n, phase=phase)
    all_nodes.append(pts)
    ring_offsets.append((start, start+n))
    start += n
all_nodes = np.vstack(all_nodes)

# jump “scale”: like musical intervals (unique but harmonic)
intervals = krng.choice([3, 5, 7, 9, 12], size=3, replace=False)

segs = []
for (a, b) in ring_offsets:
    n = b - a
    # intra-ring connections (star-like but softer)
    step = int(krng.choice(intervals))
    for i in range(n):
        j = (i + step) % n
        segs.append([all_nodes[a+i], all_nodes[a+j]])

# connections between adjacent rings (verticality)
for r in range(RINGS - 1):
    a0, a1 = ring_offsets[r]
    b0, b1 = ring_offsets[r+1]
    na = a1-a0
    nb = b1-b0
    links = int(min(na, nb) * 0.35)
    for _ in range(links):
        i = int(krng.integers(0, na))
        j = int((i/na)*nb + krng.integers(-2, 3))
        j = int(np.clip(j, 0, nb-1))
        segs.append([all_nodes[a0+i], all_nodes[b0+j]])

ax.add_collection(LineCollection(
    segs, colors=[INK], linewidths=LW_FINE, alpha=A_FINE*0.9
))

# ==================================
# 4) CENTRAL SIGIL (KEY-DRIVEN)
# ==================================
# sigil: take a sequence of points and connect them deterministically
sig_n = int(np.clip(len(KEY), 10, 40))
sig_r = R0 * 0.75
sig_pts = polar_points(sig_r, sig_n, phase=krng.uniform(0, 2*np.pi))

# pseudo-encrypted path: jumps based on KEY bytes
bytes_key = np.frombuffer(KEY.encode("utf-8"), dtype=np.uint8)
jump = int(np.clip(bytes_key.mean() / 7, 2, 11))
path = [0]
used = set(path)
for t in range(sig_n-1):
    nxt = (path[-1] + jump + int(bytes_key[t % len(bytes_key)] % 5)) % sig_n
    # avoid trivial loops
    if nxt in used:
        nxt = (nxt + 1) % sig_n
    path.append(nxt)
    used.add(nxt)

sig_segs = [[sig_pts[path[i]], sig_pts[path[i+1]]] for i in range(len(path)-1)]
ax.add_collection(LineCollection(
    sig_segs, colors=[INK], linewidths=LW_MAIN*1.15, alpha=A_MAIN
))
# central circle
ax.add_patch(Circle((0, 0), R0*0.22, fill=False, edgecolor=INK, lw=LW_MAIN, alpha=A_MAIN))

# ==================================
# INQUADRATURA + EXPORT
# ==================================
extent = R0 * 5.0
ax.set_xlim(-extent, extent)
ax.set_ylim(-extent, extent)
plt.tight_layout(pad=0)

fig.savefig(OUT_DIR / "06_cipher_mandala.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

# Export PNG:
# fig.savefig("sacred_cipher_mandala.png", dpi=300, facecolor=BG, bbox_inches="tight", pad_inches=0.02)
# Export SVG (vettoriale):
# fig.savefig("sacred_cipher_mandala.svg", facecolor

