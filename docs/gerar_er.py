"""
Gera a figura do Modelo Conceitual (MER) da Locadora de Veículos.
MAE016 — 2026.1
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# ─────────────────────────────────────────────
# LAYOUT: posição central (x, y) de cada entidade
# ─────────────────────────────────────────────
ENTITIES = {
    # nome              : (cx,  cy,  largura, altura)
    "EMPRESA"           : ( 3.5, 18.5, 3.2, 0.8),
    "PATIO"             : ( 3.5, 16.0, 3.2, 0.8),
    "VAGA"              : ( 3.5, 13.5, 3.2, 0.8),

    "GRUPO_VEICULO"     : ( 9.5, 18.5, 3.6, 0.8),
    "VEICULO"           : ( 9.5, 16.0, 3.2, 0.8),
    "ACESSORIO"         : (14.5, 16.0, 3.2, 0.8),
    "VEI_ACESS"         : (12.0, 14.5, 3.6, 0.7),  # associativa
    "FOTO"              : (14.5, 18.5, 3.2, 0.8),
    "PRONTUARIO"        : ( 9.5, 13.5, 3.4, 0.8),

    "CLIENTE"           : ( 3.5, 10.5, 3.2, 0.8),
    "CLIENTE_PF"        : ( 1.0,  8.2, 3.2, 0.8),
    "CLIENTE_PJ"        : ( 5.8,  8.2, 3.2, 0.8),
    "CONDUTOR"          : ( 3.5,  5.8, 3.2, 0.8),

    "RESERVA"           : ( 9.5, 10.5, 3.2, 0.8),
    "FILA_ESPERA"       : (14.5, 10.5, 3.4, 0.8),

    "LOCACAO"           : ( 9.5,  7.8, 3.2, 0.8),
    "PROT_ADIC"         : (14.5,  7.8, 3.6, 0.8),
    "LOC_PROT"          : (12.0,  5.8, 3.6, 0.7),  # associativa
    "COBRANCA"          : ( 9.5,  5.8, 3.2, 0.8),
    "VEICULO_PATIO"     : ( 3.5,  3.0, 3.6, 0.8),
}

# Entidades associativas (losango)
ASSOCIATIVE = {"VEI_ACESS", "LOC_PROT"}

# Subtipos (herança) — linha tracejada
SUBTYPES = {"CLIENTE_PF", "CLIENTE_PJ"}

# ─────────────────────────────────────────────
# ARESTAS: (origem, destino, label, cardinalidade)
# cardinalidade: "1N" | "NN" | "11" | "10"
# ─────────────────────────────────────────────
EDGES = [
    # Empresa / Pátio / Vaga
    ("EMPRESA",      "PATIO",        "possui",               "1N"),
    ("EMPRESA",      "VEICULO",      "proprietária",         "1N"),
    ("PATIO",        "VAGA",         "contém",               "1N"),

    # Grupo / Veículo / Acessório
    ("GRUPO_VEICULO","VEICULO",      "classifica",           "1N"),
    ("VEICULO",      "VEI_ACESS",    "",                     "1N"),
    ("ACESSORIO",    "VEI_ACESS",    "",                     "1N"),
    ("VEICULO",      "FOTO",         "possui",               "1N"),
    ("VEICULO",      "PRONTUARIO",   "possui",               "1N"),

    # Cliente / herança
    ("CLIENTE",      "CLIENTE_PF",   "é",                    "IS-A"),
    ("CLIENTE",      "CLIENTE_PJ",   "é",                    "IS-A"),
    ("CLIENTE_PF",   "CONDUTOR",     "pode ser",             "1N"),
    ("CLIENTE_PJ",   "CONDUTOR",     "autoriza",             "1N"),

    # Reserva / Fila
    ("CLIENTE",      "RESERVA",      "realiza",              "1N"),
    ("GRUPO_VEICULO","RESERVA",      "solicitado",           "1N"),
    ("PATIO",        "RESERVA",      "retirada/devolução",   "1N"),
    ("CLIENTE",      "FILA_ESPERA",  "entra",                "1N"),
    ("GRUPO_VEICULO","FILA_ESPERA",  "aguardado",            "1N"),

    # Locação
    ("RESERVA",      "LOCACAO",      "origina",              "10"),
    ("CLIENTE",      "LOCACAO",      "contrata",             "1N"),
    ("CONDUTOR",     "LOCACAO",      "conduz",               "1N"),
    ("VEICULO",      "LOCACAO",      "alugado",              "1N"),
    ("PATIO",        "LOCACAO",      "saída/chegada",        "1N"),

    # Locação × Proteção
    ("LOCACAO",      "LOC_PROT",     "",                     "1N"),
    ("PROT_ADIC",    "LOC_PROT",     "",                     "1N"),

    # Cobrança
    ("LOCACAO",      "COBRANCA",     "gera",                 "1N"),

    # Veículo_Pátio
    ("VEICULO",      "VEICULO_PATIO","posicionado",          "1N"),
    ("VAGA",         "VEICULO_PATIO","ocupa",                "1N"),
    ("LOCACAO",      "VEICULO_PATIO","registra",             "1N"),

    # Foto ← Locação
    ("LOCACAO",      "FOTO",         "documenta",            "1N"),
]

# ─────────────────────────────────────────────
# CORES
# ─────────────────────────────────────────────
C_ENTITY   = "#2563EB"   # azul entidade
C_ASSOC    = "#7C3AED"   # roxo entidade associativa
C_SUBTYPE  = "#0891B2"   # ciano subtipo
C_TEXT     = "#FFFFFF"
C_EDGE     = "#374151"
C_ISA      = "#0891B2"
C_BG       = "#F8FAFC"

ATTR_COLORS = {
    "EMPRESA":       "#DBEAFE",
    "PATIO":         "#DBEAFE",
    "VAGA":          "#DBEAFE",
    "GRUPO_VEICULO": "#EDE9FE",
    "VEICULO":       "#EDE9FE",
    "ACESSORIO":     "#EDE9FE",
    "VEI_ACESS":     "#F3E8FF",
    "FOTO":          "#EDE9FE",
    "PRONTUARIO":    "#EDE9FE",
    "CLIENTE":       "#DCFCE7",
    "CLIENTE_PF":    "#A7F3D0",
    "CLIENTE_PJ":    "#A7F3D0",
    "CONDUTOR":      "#DCFCE7",
    "RESERVA":       "#FEF3C7",
    "FILA_ESPERA":   "#FEF3C7",
    "LOCACAO":       "#FEE2E2",
    "PROT_ADIC":     "#FCE7F3",
    "LOC_PROT":      "#FDF4FF",
    "COBRANCA":      "#FEE2E2",
    "VEICULO_PATIO": "#E0F2FE",
}

DISPLAY_NAMES = {
    "VEI_ACESS"    : "VEI_ACESS\n(N:N)",
    "LOC_PROT"     : "LOC_PROT\n(N:N)",
    "VEICULO_PATIO": "VEICULO\nPATIO",
    "GRUPO_VEICULO": "GRUPO\nVEICULO",
    "FILA_ESPERA"  : "FILA\nESPERA",
    "PROT_ADIC"    : "PROTECAO\nADICIONAL",
    "PRONTUARIO"   : "PRONTUARIO\nVEICULO",
    "CLIENTE_PF"   : "CLIENTE\nPF",
    "CLIENTE_PJ"   : "CLIENTE\nPJ",
}


def get_center(name):
    x, y, w, h = ENTITIES[name]
    return x, y


def draw_entity(ax, name, x, y, w, h):
    color = ATTR_COLORS.get(name, "#E5E7EB")

    if name in ASSOCIATIVE:
        # Losango
        pts = [(x, y + h/2), (x + w/2, y), (x, y - h/2), (x - w/2, y)]
        diamond = plt.Polygon(pts, closed=True,
                              facecolor=color, edgecolor="#4B5563",
                              linewidth=1.5, zorder=3)
        ax.add_patch(diamond)
        label = DISPLAY_NAMES.get(name, name)
        ax.text(x, y, label, ha="center", va="center",
                fontsize=6.5, fontweight="bold", color="#1F2937", zorder=4,
                multialignment="center")
    else:
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                              boxstyle="round,pad=0.06",
                              facecolor=color, edgecolor="#4B5563",
                              linewidth=1.5, zorder=3)
        ax.add_patch(rect)
        label = DISPLAY_NAMES.get(name, name)
        ax.text(x, y, label, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color="#1F2937", zorder=4,
                multialignment="center")


def edge_point(name, tx, ty):
    """Return the border point of entity `name` closest to (tx, ty)."""
    cx, cy, w, h = ENTITIES[name]
    dx = tx - cx
    dy = ty - cy
    if abs(dx) == 0 and abs(dy) == 0:
        return cx, cy
    # intersect ray with rectangle
    if abs(dx) > 1e-9:
        tx_hit = (w/2) / abs(dx)
    else:
        tx_hit = 1e9
    if abs(dy) > 1e-9:
        ty_hit = (h/2) / abs(dy)
    else:
        ty_hit = 1e9
    t = min(tx_hit, ty_hit)
    return cx + dx * t, cy + dy * t


def draw_edge(ax, src, dst, label, card):
    sx, sy = get_center(src)
    dx, dy = get_center(dst)

    # ISA: dashed
    linestyle = "--" if card == "IS-A" else "-"
    color     = C_ISA if card == "IS-A" else C_EDGE

    # compute border attachment points
    bsx, bsy = edge_point(src, dx, dy)
    bdx, bdy = edge_point(dst, sx, sy)

    ax.annotate("", xy=(bdx, bdy), xytext=(bsx, bsy),
                arrowprops=dict(arrowstyle="->" if card != "IS-A" else "-",
                                color=color, lw=1.2,
                                linestyle=linestyle,
                                connectionstyle="arc3,rad=0.0"),
                zorder=2)

    if label:
        mx = (bsx + bdx) / 2
        my = (bsy + bdy) / 2
        ax.text(mx, my, label, fontsize=5.5, color="#6B7280",
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white",
                          ec="none", alpha=0.85),
                zorder=5)

    # cardinality symbols
    SYMBOLS = {"1N": ("1", "N"), "NN": ("N", "M"), "11": ("1", "1"),
               "10": ("1", "0..1"), "IS-A": ("", "")}
    s1, s2 = SYMBOLS.get(card, ("", ""))

    def offset_text(bx, by, cx, cy, text, offset=0.28):
        length = ((cx - bx)**2 + (cy - by)**2)**0.5 or 1
        ux = (cx - bx) / length
        uy = (cy - by) / length
        ax.text(bx + ux * offset, by + uy * offset, text,
                fontsize=6, color="#1D4ED8", fontweight="bold",
                ha="center", va="center", zorder=6)

    if s1:
        offset_text(bsx, bsy, bdx, bdy, s1)
    if s2:
        offset_text(bdx, bdy, bsx, bsy, s2)


# ─────────────────────────────────────────────
# FIGURA
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(20, 22))
ax.set_facecolor(C_BG)
fig.patch.set_facecolor(C_BG)
ax.set_xlim(-0.5, 19)
ax.set_ylim(1.5, 20.5)
ax.axis("off")

# Título
ax.text(9.25, 20.1,
        "Modelo Conceitual (MER) — Sistema de Locação de Veículos",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color="#1E3A5F")
ax.text(9.25, 19.7,
        "MAE016 — 2026.1 | Grupo: [NOMES E DRE]",
        ha="center", va="center", fontsize=9, color="#64748B")

# Linha separadora
ax.axhline(19.4, color="#CBD5E1", lw=0.8)

# Desenhar arestas primeiro (atrás)
for src, dst, label, card in EDGES:
    draw_edge(ax, src, dst, label, card)

# Desenhar entidades depois (na frente)
for name, (cx, cy, w, h) in ENTITIES.items():
    draw_entity(ax, name, cx, cy, w, h)

# Legenda
legend_x, legend_y = 0.0, 3.5
legend_items = [
    (FancyBboxPatch((0, 0), 1, 0.4, boxstyle="round,pad=0.05",
                    facecolor="#DBEAFE", edgecolor="#4B5563", lw=1.2),
     "Entidade"),
    (FancyBboxPatch((0, 0), 1, 0.4, boxstyle="round,pad=0.05",
                    facecolor="#F3E8FF", edgecolor="#4B5563", lw=1.2),
     "Entidade Associativa (N:N)"),
    (FancyBboxPatch((0, 0), 1, 0.4, boxstyle="round,pad=0.05",
                    facecolor="#A7F3D0", edgecolor="#4B5563", lw=1.2),
     "Subtipo (herança)"),
    (mpatches.Patch(facecolor="none", edgecolor=C_EDGE, lw=1.2),
     "Relacionamento 1:N"),
    (mpatches.Patch(facecolor="none", edgecolor=C_ISA,  lw=1.2,
                    linestyle="--"),
     "IS-A (herança)"),
]

for i, (patch, txt) in enumerate(legend_items):
    ax.add_patch(mpatches.FancyBboxPatch(
        (legend_x - 0.1, legend_y - i * 0.55 - 0.2), 0.5, 0.35,
        boxstyle="round,pad=0.04",
        facecolor=patch.get_facecolor() if hasattr(patch, "get_facecolor") else "white",
        edgecolor="#9CA3AF", lw=0.8, zorder=6))
    ax.text(legend_x + 0.55, legend_y - i * 0.55 - 0.02, txt,
            fontsize=7, va="center", color="#374151", zorder=7)

ax.text(legend_x + 0.2, legend_y + 0.4, "Legenda",
        fontsize=8, fontweight="bold", color="#374151")

plt.tight_layout(pad=0.5)
out = "/Users/mei/dev/ufrj/big-data/docs/modelo_conceitual.png"
plt.savefig(out, dpi=180, bbox_inches="tight",
            facecolor=C_BG, edgecolor="none")
plt.close()
print(f"Saved: {out}")
