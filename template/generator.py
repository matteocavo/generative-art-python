"""
Phyllotaxis Generator
Parametric generator: density (low|mid|high), mood (ritual|techno|minimal), gates (square|octagon|none)
"""

import os, pathlib
OUT_DIR = pathlib.Path(__file__).parent.parent / "img"
OUT_DIR.mkdir(exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle

# =========================
# GENERATOR SETTINGS
# =========================
SEED = 303
BG, INK = "black", "white"

density = "low"                 # "low" | "mid" | "high"
mood = "ritual"                 # FIX: era "fitual"
gates = "none"                  # "square" | "octagon" | "none"

DPI, FIGSIZE = 280, (8, 8)
R0 = 1.0

rng = np.random.default_rng(SEED)

# =========================
# PRESET MAP
# =========================
PRESETS = {
    "low":  dict(N=700,  CHORDS=950,  DOT_STEP=10),
    "mid":  dict(N=1200, CHORDS=2200, DOT_STEP=6),
    "high": dict(N=2000, CHORDS=4200, DOT_STEP=4),
}
P = PRESETS[density]

if mood == "ritual":
    LW_MAIN, LW_FINE = 1.10, 0.48
    A_MAIN, A_FINE = 0.80, 0.20
    RINGS = 7
    RING_ALPHA = 0.18
elif mood == "techno":
    LW_MAIN, LW_FINE = 1.05, 0.42
    A_MAIN, A_FINE = 0.70, 0.14
    RINGS = 9
    RING_ALPHA = 0.12
else:  # minimal
    LW_MAIN, LW_FINE = 1.15, 0.52
    A_MAIN, A_FINE = 0.75, 0.10
    RINGS = 5
    RING_ALPHA = 0.10

SPIRAL_MAX = R0 * 4.75

# =========================
# HELPERS
# =========================
def phyllotaxis_points(N, max_r):
    phi = (1 + 5**0.5) / 2
    golden_angle = 2*np.pi*(1 - 1/phi)

    i = np.arange(N)
    r = max_r * np.sqrt(i / (N-1))
    theta = i * golden_angle
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    return np.column_stack([x, y]), r, theta

def draw_gates(ax, S, kind):
    if kind == "none":
        return
    if kind == "square":
        poly = np.array([[-S,-S],[S,-S],[S,S],[-S,S],[-S,-S]])
        ax.plot(poly[:,0], poly[:,1], color=INK, lw=LW_MAIN, alpha=A_MAIN*0.35)
        ax.plot([-S,S],[-S,S], color=INK, lw=LW_FINE, alpha=A_FINE)
        ax.plot([-S,S],[S,-S], color=INK, lw=LW_FINE, alpha=A_FINE)
        G = S*0.62
        ax.plot([-G,G],[0,0], color=INK, lw=LW_MAIN, alpha=A_MAIN*0.35)
        ax.plot([0,0],[-G,G], color=INK, lw=LW_MAIN, alpha=A_MAIN*0.35)
        return

    t = np.linspace(0, 2*np.pi, 9)
    octa = np.column_stack([S*np.cos(t), S*np.sin(t)])
    ax.plot(octa[:,0], octa[:,1], color=INK, lw=LW_MAIN, alpha=A_MAIN*0.32)
    ax.plot([-S,S],[0,0], color=INK, lw=LW_FINE, alpha=A_FINE*0.9)
    ax.plot([0,0],[-S,S], color=INK, lw=LW_FINE, alpha=A_FINE*0.9)

def constellation_chords(pts, r, theta, n_chords):
    N = len(pts)
    segs = []

    # 1) local chords
    idx = rng.integers(0, N, size=int(n_chords*0.78))
    for a in idx:
        target_r = r[a] + rng.normal(0, SPIRAL_MAX*0.035)
        b = int(np.clip(np.searchsorted(r, target_r), 0, N-1))
        b = (b + int(rng.integers(25, 180))) % N
        segs.append([pts[a], pts[b]])

    # 2) long chords
    idx2 = rng.integers(0, N, size=int(n_chords*0.22))
    for a in idx2:
        b = (a + int(rng.integers(N*0.18, N*0.45))) % N
        if r[a] < SPIRAL_MAX*0.35 and rng.random() < 0.65:
            continue
        segs.append([pts[a], pts[b]])

    return segs

# =========================
# SIGNATURE (INVISIBLE, DOES NOT CHANGE LOOK)
# =========================
SIGNATURE = "Aumaaz"

def signature_rng(signature: str, seed: int):
    # deterministic RNG from string (FNV-1a style, simple)
    h = 2166136261
    for c in signature.encode("utf-8"):
        h ^= c
        h = (h * 16777619) & 0xffffffff
    return np.random.default_rng((h ^ seed) & 0xffffffff)

def add_signature_segs(pts, r, base_extent, signature, n_sig=60):
    """
    Adds very few signed lines at low alpha.
    Visually almost invisible, but the network contains the signature.
    """
    srng = signature_rng(signature, SEED)
    N = len(pts)
    segs = []

    # choose mostly mid-outer points to avoid a “blob” at the center
    candidates = np.where(r > base_extent*0.35)[0]
    if len(candidates) < 10:
        candidates = np.arange(N)

    cursor = int(srng.integers(0, len(candidates)))
    jumps = srng.integers(17, 97, size=n_sig)  # pattern dipendente dalla firma

    for j in jumps:
        a = candidates[cursor % len(candidates)]
        b = candidates[(cursor + j) % len(candidates)]
        segs.append([pts[a], pts[b]])
        cursor += j

    return segs

# =========================
# RENDER
# =========================
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_aspect("equal")
ax.axis("off")

pts, r, theta = phyllotaxis_points(P["N"], SPIRAL_MAX)

# Cerchi guida
for rr in np.linspace(R0*1.0, R0*4.95, RINGS):
    ax.add_patch(Circle((0,0), rr, fill=False, edgecolor=INK, lw=LW_FINE, alpha=RING_ALPHA))

# Micro-nodi
dot_step = P["DOT_STEP"]
for k in range(0, len(pts), dot_step):
    base = 0.010 if mood != "techno" else 0.008
    grow = 0.020 if mood == "ritual" else 0.016
    rr = (base + grow*(r[k]/SPIRAL_MAX)) * R0
    ax.add_patch(Circle((pts[k,0], pts[k,1]), rr, fill=False,
                        edgecolor=INK, lw=LW_FINE, alpha=A_FINE*1.15))

# Temple gates
S = R0 * 4.55
draw_gates(ax, S, gates)

# Chords base (IDENTICI al tuo stile)
segs = constellation_chords(pts, r, theta, P["CHORDS"])
ax.add_collection(LineCollection(segs, colors=[INK], linewidths=LW_FINE, alpha=A_FINE*0.90))

# Firma: linee extra quasi invisibili (non cambia il look)
sig_segs = add_signature_segs(pts, r, SPIRAL_MAX, SIGNATURE, n_sig=60)
ax.add_collection(LineCollection(sig_segs, colors=[INK], linewidths=LW_FINE, alpha=A_FINE*0.10))

# Crosshair (come nel tuo output originale: attivo se non minimal)
if mood != "minimal":
    ax.plot([-R0*5.1, R0*5.1], [0,0], color=INK, lw=LW_FINE, alpha=A_FINE*0.8)
    ax.plot([0,0], [-R0*5.1, R0*5.1], color=INK, lw=LW_FINE, alpha=A_FINE*0.8)

# Sigillo centrale: RIMOSSO (questo era il “cerchio più scuro”)
# ax.add_patch(Circle((0,0), R0*0.24, fill=False, edgecolor=INK, lw=LW_MAIN, alpha=A_MAIN))
# ax.add_patch(Circle((0,0), R0*0.58, fill=False, edgecolor=INK, lw=LW_FINE, alpha=A_FINE))

extent = R0*5.25
ax.set_xlim(-extent, extent); ax.set_ylim(-extent, extent)
plt.tight_layout(pad=0)
plt.show()

# Export:
fig.savefig(OUT_DIR / f"generator_{density}_{mood}_{gates}.png", dpi=300, facecolor=BG, bbox_inches="tight", pad_inches=0.02)
# fig.savefig("phyllotaxis_temple_signed.svg", facecolor=BG, bbox_inches="tight", pad_inches=0.02)
