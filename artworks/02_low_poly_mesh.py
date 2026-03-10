"""
Low Poly Mesh
Jittered triangulated grid with flat shading and linear hatching
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection

rng = np.random.default_rng(5)

W, H = 900, 1300
fig, ax = plt.subplots(figsize=(6, 9), dpi=220)
ax.set_xlim(0, W); ax.set_ylim(0, H)
ax.axis("off")
fig.patch.set_facecolor("black")
ax.set_facecolor("black")

# simple “mesh”: jittered grid -> quads split into triangles
nx, ny = 9, 14
xs = np.linspace(80, W-80, nx)
ys = np.linspace(120, H-120, ny)
grid = np.array([(x, y) for y in ys for x in xs], float)
grid += rng.normal(0, 22, grid.shape)

# grid indices
def idx(i, j): return j*nx + i

polys = []
for j in range(ny-1):
    for i in range(nx-1):
        a = grid[idx(i, j)]
        b = grid[idx(i+1, j)]
        c = grid[idx(i+1, j+1)]
        d = grid[idx(i, j+1)]
        # random split
        if rng.random() < 0.5:
            polys += [np.array([a, b, c]), np.array([a, c, d])]
        else:
            polys += [np.array([a, b, d]), np.array([b, c, d])]

# fake light
light = np.array([0.7, 0.2])  # direzione luce (x,y)
light = light / np.linalg.norm(light)

for P in polys:
    # 2D normal: use main edge to estimate “orientation”
    e = P[1] - P[0]
    n = np.array([-e[1], e[0]])
    n = n / (np.linalg.norm(n) + 1e-9)
    shade = np.clip((n @ light) * 0.6 + 0.55, 0.15, 0.95)  # 0..1
    face = (shade, shade, shade)

    patch = Polygon(P, closed=True, facecolor=face, edgecolor=(1,1,1,0.06), lw=0.8)
    ax.add_patch(patch)

    # linear hatching clipped to the polygon
    angle = rng.uniform(-1.2, 1.2)
    spacing = rng.uniform(5, 10)

    # bounding box
    minx, miny = P.min(axis=0); maxx, maxy = P.max(axis=0)
    L = max(maxx-minx, maxy-miny) * 2

    # generate parallel lines
    lines = []
    t_vals = np.arange(-L, L, spacing)
    for t in t_vals:
        # base line in local coords, then rotate
        x0, y0 = -L, t
        x1, y1 =  L, t
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle),  np.cos(angle)]])
        center = np.array([(minx+maxx)/2, (miny+maxy)/2])
        p0 = (R @ np.array([x0, y0])) + center
        p1 = (R @ np.array([x1, y1])) + center
        lines.append([p0, p1])

    lc = LineCollection(lines, colors=[(1,1,1,0.09)], linewidths=0.6)
    lc.set_clip_path(patch)
    ax.add_collection(lc)

plt.tight_layout(pad=0)
fig.savefig(OUT_DIR / "02_low_poly_mesh.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

