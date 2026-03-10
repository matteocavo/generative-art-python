"""
Torus Knot Mandala
2D projection of torus knots on guide circles
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle

SEED = 202
BG, INK = "black", "white"
DPI, FIGSIZE = 280, (8, 8)

R0 = 1.0
LAYERS = 6
SAMPLES = 1800
LW_MAIN = 1.05
LW_FINE = 0.50
A_MAIN = 0.78
A_FINE = 0.22

rng = np.random.default_rng(SEED)

fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_aspect("equal")
ax.axis("off")

# guide circles
for rr in np.linspace(R0*0.9, R0*4.9, 7):
    ax.add_patch(Circle((0,0), rr, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE))

# Knot parameters (p,q): changes the knot identity
p = int(rng.integers(2, 6))
q = int(rng.integers(5, 11))

t = np.linspace(0, 2*np.pi, SAMPLES)
all_segs = []

for i in range(LAYERS):
    # modulate radius and torus “thickness”
    R = R0*(2.4 + i*0.35)
    r = R0*(0.65 + 0.08*i)
    phase = rng.uniform(0, 2*np.pi)

    # curve: 2D stylized torus-knot (projection)
    x = (R + r*np.cos(q*t + phase)) * np.cos(p*t)
    y = (R + r*np.cos(q*t + phase)) * np.sin(p*t)

    # normalize slightly to stay within bounds
    scale = (R0*4.8) / max(np.max(np.abs(x)), np.max(np.abs(y)))
    x *= scale; y *= scale

    pts = np.column_stack([x, y])
    segs = np.stack([pts[:-1], pts[1:]], axis=1)
    all_segs.append(segs)

# draw layers (outer layers are lighter)
for i, segs in enumerate(all_segs):
    alpha = A_MAIN * (0.55 + 0.45*(i/(len(all_segs)-1)))
    lw = LW_MAIN * (0.95 if i < len(all_segs)-1 else 1.15)
    ax.add_collection(LineCollection(segs, colors=[INK], linewidths=lw, alpha=alpha))

# sacred “crosshair”
ax.plot([-R0*5, R0*5], [0,0], color=INK, lw=LW_FINE, alpha=A_FINE)
ax.plot([0,0], [-R0*5, R0*5], color=INK, lw=LW_FINE, alpha=A_FINE)

# central sigil
ax.add_patch(Circle((0,0), R0*0.22, fill=False, edgecolor=INK, lw=LW_MAIN, alpha=A_MAIN))

extent = R0*5.2
ax.set_xlim(-extent, extent); ax.set_ylim(-extent, extent)
plt.tight_layout(pad=0)
fig.savefig(OUT_DIR / "10_torus_knot_mandala.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
plt.show()

