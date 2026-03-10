"""
Curved Hatch
Delaunay triangulation with sinusoidal hatching — warm paper palette
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection

# ======================
# PARAMETERS (play here)
# ======================
W, H = 1000, 1500
N_POINTS = 140          # higher = more faces
SEED = 9                # change for variations
EDGE_ALPHA = 0.06
HATCH_ALPHA = 0.10
HATCH_LW = 0.55

# shading (contrast)
SHADE_MIN, SHADE_MAX = 0.12, 0.92
LIGHT = np.array([0.85, 0.25])  # light direction (x,y)

# warm paper palette
BG       = "#F2E8D5"                        # cream background
COL_DARK = np.array([0.18, 0.10, 0.04])   # dark sepia
COL_LIGHT= np.array([0.95, 0.88, 0.75])   # warm highlight
INK      = (0.18, 0.10, 0.04)             # ink for edges and hatching

# curved hatching
SPACING_RANGE = (6, 13)         # distance between lines
WAVY_AMPL = (0.0, 10.0)         # wave amplitude
WAVY_FREQ = (1.0, 3.0)          # wave frequency
SEGMENTS = 28                   # higher = smoother lines

rng = np.random.default_rng(SEED)
LIGHT = LIGHT / (np.linalg.norm(LIGHT) + 1e-9)

# ======================
# POINTS + TRIANGULATION
# ======================
# random points with some "border" points for a fuller shape
pts = rng.random((N_POINTS, 2))
pts[:, 0] = pts[:, 0] * (W * 0.82) + (W * 0.09)
pts[:, 1] = pts[:, 1] * (H * 0.82) + (H * 0.09)

# add a "frame" of points to avoid huge triangles at the edges
frame = []
for t in np.linspace(0, 1, 16):
    frame += [
        (W*0.08 + t*(W*0.84), H*0.08),
        (W*0.08 + t*(W*0.84), H*0.92),
        (W*0.08, H*0.08 + t*(H*0.84)),
        (W*0.92, H*0.08 + t*(H*0.84)),
    ]
pts = np.vstack([pts, np.array(frame)])

tri = mtri.Triangulation(pts[:, 0], pts[:, 1])
tris = tri.triangles

# ======================
# FIGURE
# ======================
fig, ax = plt.subplots(figsize=(6, 9), dpi=240)
ax.set_xlim(0, W); ax.set_ylim(0, H)
ax.axis("off")
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

def shade_for_triangle(P):
    # P: (3,2)
    # use an edge as direction -> 2D normal for face shading
    e = P[1] - P[0]
    n = np.array([-e[1], e[0]])
    n = n / (np.linalg.norm(n) + 1e-9)
    s = (n @ LIGHT) * 0.65 + 0.55
    return float(np.clip(s, SHADE_MIN, SHADE_MAX))

def curved_hatch_lines(P, angle, spacing, ampl, freq):
    """
    Generate many "quasi-parallel" but curved (sinusoidal) lines,
    in the triangle bounding box, then clip them to the polygon.
    """
    minx, miny = P.min(axis=0)
    maxx, maxy = P.max(axis=0)
    cx, cy = (minx+maxx)/2, (miny+maxy)/2
    L = max(maxx-minx, maxy-miny) * 2.2

    # base coords: horizontal lines y = t, then rotate
    t_vals = np.arange(-L, L, spacing)

    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])

    lines = []
    xs = np.linspace(-L, L, SEGMENTS)

    for t in t_vals:
        # undulation: y = t + ampl*sin(...)
        ys = t + ampl * np.sin((xs / L) * (freq * np.pi) + rng.uniform(0, 2*np.pi))
        pts_local = np.stack([xs, ys], axis=1)
        pts_rot = (pts_local @ R.T)
        pts_rot[:, 0] += cx
        pts_rot[:, 1] += cy

        # convert to segments for LineCollection
        segs = np.stack([pts_rot[:-1], pts_rot[1:]], axis=1)
        lines.append(segs)

    if not lines:
        return np.zeros((0, 2, 2))
    return np.concatenate(lines, axis=0)

# ======================
# DRAW: faces + hatch
# ======================
for t in tris:
    P = pts[t]  # (3,2)

    s = shade_for_triangle(P)
    face = tuple(COL_DARK + s * (COL_LIGHT - COL_DARK))

    patch = Polygon(
        P, closed=True,
        facecolor=face,
        edgecolor=(*INK, EDGE_ALPHA),
        lw=0.9
    )
    ax.add_patch(patch)

    # hatch: darker = denser (you can invert if you want)
    spacing = np.interp(s, [SHADE_MIN, SHADE_MAX], [SPACING_RANGE[0], SPACING_RANGE[1]])
    spacing *= rng.uniform(0.9, 1.15)

    angle = rng.uniform(-1.4, 1.4)  # different direction per face
    ampl = rng.uniform(*WAVY_AMPL) * np.interp(s, [SHADE_MIN, SHADE_MAX], [1.2, 0.3])
    freq = rng.uniform(*WAVY_FREQ)

    segs = curved_hatch_lines(P, angle, spacing, ampl, freq)

    lc = LineCollection(
        segs,
        colors=[(*INK, HATCH_ALPHA)],
        linewidths=HATCH_LW
    )
    lc.set_clip_path(patch)
    ax.add_collection(lc)

plt.tight_layout(pad=0)
fig.savefig(OUT_DIR / "03_curved_hatch.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

