"""
Diagrama ER — Notação Canônica de Chen — Locadora de Veículos
MAE016 — 2026.1

Convenções da notação de Chen:
  Entidade       → retângulo azul
  Relacionamento → losango amarelo
  Atributo       → elipse verde (PK = sublinhado + borda escura)
  Herança ISA    → triângulo ciano
  Cardinalidade  → rótulo 1 / N / M na linha, próximo à entidade
  Linha dupla    → participação total (todo membro participa)
"""

# ── Importações ────────────────────────────────────────────────────────────────

import matplotlib              # biblioteca principal de gráficos
matplotlib.use("Agg")          # backend sem janela (salva direto em arquivo)
import matplotlib.pyplot as plt
import numpy as np             # operações vetoriais para cálculo de bordas
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon

# Cor de fundo do canvas
BG = '#F8FAFC'

# ── Dicionários globais de dimensões ──────────────────────────────────────────
# Preenchidos durante o desenho; usados depois para calcular onde as linhas
# devem se conectar às bordas de cada forma.
ENTITY_DIMS = {}   # nome → (largura, altura) do retângulo da entidade
REL_DIMS    = {}   # nome → (cx, cy, largura, altura, tipo) do relacionamento


# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES DE GEOMETRIA
# Calculam o ponto na borda de uma forma que fica voltado para outro ponto.
# Isso garante que as linhas chegam na borda e não no centro das formas.
# ══════════════════════════════════════════════════════════════════════════════

def _rect_pt(cx, cy, w, h, tx, ty):
    """
    Retorna o ponto (x,y) na borda do retângulo centrado em (cx,cy)
    com largura w e altura h, na direção de (tx,ty).

    Estratégia: parametriza a reta (cx + dx*s, cy + dy*s) e encontra
    o menor s que toca a borda (interseção com semiplanos x = ±w/2 e y = ±h/2).
    """
    dx, dy = tx - cx, ty - cy                          # vetor de direção
    if abs(dx) + abs(dy) < 1e-9:                       # ponto coincidente
        return cx, cy
    sx = (w / 2) / abs(dx) if abs(dx) > 1e-9 else 1e9 # distância até borda lateral
    sy = (h / 2) / abs(dy) if abs(dy) > 1e-9 else 1e9 # distância até borda superior/inferior
    s = min(sx, sy)                                    # a borda mais próxima vence
    return cx + dx * s, cy + dy * s


def _diamond_pt(cx, cy, rw, rh, tx, ty):
    """
    Retorna o ponto na borda do losango centrado em (cx,cy)
    com semi-eixos rw/2 (horizontal) e rh/2 (vertical), na direção de (tx,ty).

    A equação da borda do losango é |x/a| + |y/b| = 1.
    Substituindo a reta paramétrica: t = 1 / (|dx|/a + |dy|/b).
    """
    dx, dy = tx - cx, ty - cy
    if abs(dx) + abs(dy) < 1e-9:
        return cx, cy
    denom = abs(dx) / (rw / 2) + abs(dy) / (rh / 2)  # denominador da equação
    t = 1.0 / denom if denom > 1e-9 else 1.0           # parâmetro do ponto na borda
    return cx + dx * t, cy + dy * t


def _tri_pt(cx, cy, hw, hh, tx, ty):
    """
    Aproximação para o triângulo ISA: trata como retângulo de mesma largura
    e altura. Suficiente para as linhas chegarem perto da borda correta.
    """
    return _rect_pt(cx, cy, hw * 2, hh * 1.6, tx, ty)


# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE DESENHO
# ══════════════════════════════════════════════════════════════════════════════

def draw_entity(ax, cx, cy, name, display=None):
    """
    Desenha um retângulo representando uma entidade na posição (cx, cy).

    Parâmetros:
      ax      – eixo matplotlib onde desenhar
      cx, cy  – coordenadas do centro
      name    – chave interna (usada em ENTITY_DIMS)
      display – rótulo exibido (pode ter '\n' para quebra de linha)

    Largura e altura são calculadas automaticamente pelo comprimento do texto.
    Armazena as dimensões em ENTITY_DIMS para uso posterior nos cálculos de borda.
    """
    lbl = display or name                              # rótulo a exibir
    lines = lbl.split('\n')                            # separa linhas para medir
    w = max(len(l) for l in lines) * 0.145 + 1.3      # largura proporcional ao texto
    h = 0.9 + (len(lines) - 1) * 0.38                 # altura extra por linha adicional

    # Retângulo com cantos levemente arredondados (pad mínimo)
    r = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                       boxstyle='square,pad=0.04',
                       facecolor='#BFDBFE',            # azul claro
                       edgecolor='#1D4ED8',            # azul escuro (borda)
                       linewidth=2.2, zorder=5)        # zorder alto → sobre as linhas
    ax.add_patch(r)

    # Texto centralizado no retângulo
    ax.text(cx, cy, lbl, ha='center', va='center',
            fontsize=7.5, fontweight='bold', color='#1E3A5F',
            zorder=6, multialignment='center', linespacing=1.3)

    ENTITY_DIMS[name] = (w, h)                        # salva dimensões para bordas


def draw_relationship(ax, name, cx, cy, label):
    """
    Desenha um losango representando um relacionamento na posição (cx, cy).

    O losango é um Polygon de 4 vértices (topo, direita, base, esquerda).
    Dimensões calculadas automaticamente pelo comprimento do texto.
    Armazena (cx, cy, rw, rh, 'diamond') em REL_DIMS.
    """
    lines = label.split('\n')
    rw = max(len(l) for l in lines) * 0.155 + 2.0     # largura do losango
    rh = 0.95 + (len(lines) - 1) * 0.35               # altura do losango

    # Quatro vértices do losango: topo, direita, base, esquerda
    pts = np.array([(cx, cy + rh/2), (cx + rw/2, cy),
                    (cx, cy - rh/2), (cx - rw/2, cy)])
    ax.add_patch(Polygon(pts, closed=True,
                         facecolor='#FDE68A',          # amarelo claro
                         edgecolor='#B45309',          # laranja escuro
                         lw=2.0, zorder=5))

    # Texto centrado no losango
    ax.text(cx, cy, label, ha='center', va='center',
            fontsize=5.8, fontweight='bold', color='#78350F',
            zorder=6, multialignment='center', linespacing=1.2)

    REL_DIMS[name] = (cx, cy, rw, rh, 'diamond')      # salva para cálculo de bordas


def draw_isa(ax, name, cx, cy):
    """
    Desenha um triângulo representando herança ISA na posição (cx, cy).

    Notação de Chen: triângulo com vértice apontando para cima.
    A linha do supertipo chega ao topo; as dos subtipos saem da base.
    Armazena (cx, cy, hw*2, hh*1.45, 'triangle') em REL_DIMS.
    """
    hw, hh = 0.85, 0.72                                # semi-largura e semi-altura

    # Três vértices: topo (centro), base-esquerda, base-direita
    pts = np.array([(cx, cy + hh),
                    (cx - hw, cy - hh * 0.45),
                    (cx + hw, cy - hh * 0.45)])
    ax.add_patch(Polygon(pts, closed=True,
                         facecolor='#BAE6FD',          # ciano claro
                         edgecolor='#0369A1',          # ciano escuro
                         lw=1.8, zorder=5))

    ax.text(cx, cy + 0.1, 'ISA', ha='center', va='center',
            fontsize=5.5, fontweight='bold', color='#0369A1', zorder=6)

    REL_DIMS[name] = (cx, cy, hw * 2, hh * 1.45, 'triangle')


def draw_attr(ax, ex, ey, ax2, ay, label, pk=False):
    """
    Desenha uma elipse representando um atributo em (ax2, ay),
    conectada à entidade em (ex, ey) por uma linha fina.

    Se pk=True:
      - Borda mais escura e espessa
      - Texto em negrito
      - Linha de sublinhado manual (convenção Chen para PK)
    """
    # Linha fina conectando entidade ao atributo
    ax.plot([ex, ax2], [ey, ay], color='#9CA3AF', lw=0.85, zorder=2)

    # Largura da elipse proporcional ao comprimento do texto
    w = max(len(label) * 0.118 + 0.75, 1.5)

    e = Ellipse((ax2, ay), w, 0.58,
                facecolor='#DCFCE7' if pk else '#F0FFF4',   # PK = verde mais escuro
                edgecolor='#14532D' if pk else '#15803D',
                linewidth=1.6 if pk else 0.9, zorder=4)
    ax.add_patch(e)

    ax.text(ax2, ay, label, ha='center', va='center',
            fontsize=5.2, color='#14532D', zorder=5,
            fontweight='bold' if pk else 'normal')

    if pk:
        # Sublinhado manual: segmento horizontal sob o texto
        tw = len(label) * 0.049                         # metade da largura do texto
        ax.plot([ax2 - tw, ax2 + tw], [ay - 0.135, ay - 0.135],
                color='#14532D', lw=1.0, zorder=6)


def rel_attr(ax, rx, ry, ax2, ay, label):
    """
    Desenha um atributo pendurado em um RELACIONAMENTO (não numa entidade).
    Usado quando um relacionamento possui atributo próprio
    (ex: 'valor_cobrado_diaria' em 'contrata proteção').
    Elipse com cor amarelada para distinguir dos atributos de entidade.
    """
    ax.plot([rx, ax2], [ry, ay], color='#9CA3AF', lw=0.85, zorder=2)
    w = max(len(label) * 0.118 + 0.75, 1.5)
    e = Ellipse((ax2, ay), w, 0.58,
                facecolor='#FEF9C3',                    # amarelo muito claro
                edgecolor='#A16207',
                linewidth=0.9, zorder=4)
    ax.add_patch(e)
    ax.text(ax2, ay, label, ha='center', va='center',
            fontsize=5.2, color='#78350F', zorder=5)


def connect_er(ax, p1, p2, card='', dbl=False, color='#475569', style='-'):
    """
    Desenha a linha entre dois pontos (p1 e p2) com cardinalidade opcional.

    dbl=True  → linha dupla (participação total na notação de Chen):
                 calcula um vetor perpendicular à linha e desenha um segundo
                 segmento paralelo deslocado 0.1 unidades.
    card      → texto de cardinalidade ('1', 'N', 'M', '0..1') posicionado
                 a 88% do caminho (perto da ponta da entidade destino).
    """
    x1, y1 = p1
    x2, y2 = p2

    # Linha principal
    ax.plot([x1, x2], [y1, y2], color=color, lw=1.25,
            linestyle=style, zorder=2, solid_capstyle='round')

    if dbl:
        # Vetor perpendicular normalizado para deslocar a segunda linha
        dx, dy = x2 - x1, y2 - y1
        L = np.hypot(dx, dy)                            # comprimento do segmento
        if L > 0:
            px, py = -dy / L * 0.1, dx / L * 0.1       # perpendicular de magnitude 0.1
            ax.plot([x1 + px, x2 + px], [y1 + py, y2 + py],
                    color=color, lw=1.25, zorder=2)

    if card:
        # Posição do rótulo de cardinalidade: 88% ao longo da linha
        t = 0.88
        bx, by = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        ax.text(bx, by, card, fontsize=7.5, fontweight='bold',
                color='#1D4ED8', ha='center', va='center', zorder=8,
                bbox=dict(boxstyle='round,pad=0.06', fc='white',
                          ec='none', alpha=0.95))         # fundo branco evita sobreposição


def link_rel_ent(ax, rel_name, ent_name, card='', dbl=False):
    """
    Conecta um relacionamento (identificado por rel_name) a uma entidade
    (identificada por ent_name), calculando os pontos exatos nas bordas
    de cada forma para que a linha não sobreponha o interior das formas.

    Fluxo:
      1. Recupera dimensões do relacionamento em REL_DIMS
      2. Recupera posição e dimensões da entidade em E e ENTITY_DIMS
      3. Calcula ponto na borda do relacionamento voltado para a entidade
      4. Calcula ponto na borda da entidade voltado para o relacionamento
      5. Chama connect_er para desenhar a linha entre esses dois pontos
    """
    rx, ry, rw, rh, rtype = REL_DIMS[rel_name]         # dados do relacionamento
    ex, ey = E[ent_name]                                 # centro da entidade
    ew, eh = ENTITY_DIMS[ent_name]                       # dimensões da entidade

    # Ponto de saída na borda do relacionamento (losango ou triângulo)
    if rtype == 'diamond':
        rp = _diamond_pt(rx, ry, rw, rh, ex, ey)
    else:
        rp = _tri_pt(rx, ry, rw / 2, rh / 1.45, ex, ey)

    # Ponto de chegada na borda do retângulo da entidade
    ep = _rect_pt(ex, ey, ew, eh, rx, ry)

    connect_er(ax, rp, ep, card=card, dbl=dbl)


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DO CANVAS
# ══════════════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(46, 60))  # largura × altura em polegadas (alta resolução)
fig.patch.set_facecolor(BG)               # cor de fundo da figura
ax.set_facecolor(BG)                      # cor de fundo do eixo
ax.set_xlim(-0.5, 46)                     # limite horizontal do sistema de coordenadas
ax.set_ylim(-2, 61)                       # limite vertical (y=0 embaixo, y=61 em cima)
ax.axis('off')                            # oculta eixos cartesianos (não queremos grades)

# ── Títulos ───────────────────────────────────────────────────────────────────
ax.text(22.5, 60.2, 'Modelo Entidade-Relacionamento  —  Notação Canônica de Chen',
        ha='center', va='center', fontsize=15, fontweight='bold', color='#1E3A5F')
ax.text(22.5, 59.3,
        'MAE016 — 2026.1  ·  Locadora de Veículos  ·  Grupo: [NOMES E DRE]',
        ha='center', va='center', fontsize=9, color='#64748B')
ax.axhline(58.7, color='#CBD5E1', lw=0.8)   # linha separadora sob o título


# ── Rótulos de seções ─────────────────────────────────────────────────────────
def section(ax, x, y, txt):
    """Desenha um rótulo cinza itálico para identificar visualmente cada zona."""
    ax.text(x, y, txt, fontsize=8, color='#94A3B8', style='italic',
            ha='left', va='top',
            bbox=dict(boxstyle='round,pad=0.3', fc='#F1F5F9',
                      ec='#CBD5E1', lw=0.7))

# Cada seção agrupa entidades de um mesmo subsistema do modelo
section(ax,  0.2, 57.5, 'Infraestrutura')   # EMPRESA, PATIO, VAGA
section(ax, 16.5, 57.5, 'Frota')            # GRUPO_VEICULO, VEICULO, PRONTUARIO
section(ax, 33.5, 57.5, 'Docs / Frota')     # ACESSORIO, FOTO
section(ax,  0.2, 33.5, 'Clientes')         # CLIENTE, CLIENTE_PF, CLIENTE_PJ
section(ax, 16.5, 33.5, 'Reservas')         # RESERVA
section(ax, 33.5, 33.5, 'Fila')             # FILA_ESPERA
section(ax,  0.2, 19.0, 'Condutores')       # CONDUTOR
section(ax, 16.5, 19.0, 'Locacao')          # LOCACAO, VEICULO_PATIO, COBRANCA
section(ax, 33.5, 19.0, 'Protecoes')        # PROT_ADIC


# ══════════════════════════════════════════════════════════════════════════════
# POSIÇÕES DAS ENTIDADES
# Coordenadas (cx, cy) do centro de cada entidade no sistema do canvas.
# Layout em grade de 3 colunas (x ≈ 6, 22, 38) e 6 linhas (y = 54..16).
# ══════════════════════════════════════════════════════════════════════════════
E = {
    # Coluna 1 (x=6): infraestrutura / clientes / condutores
    'EMPRESA':         ( 6.0, 54.0),
    'PATIO':           ( 6.0, 46.0),
    'VAGA':            ( 6.0, 38.0),
    'CLIENTE':         ( 6.0, 30.0),
    'CLIENTE_PF':      ( 2.5, 23.0),
    'CLIENTE_PJ':      (11.5, 23.0),
    'CONDUTOR':        ( 6.0, 16.0),

    # Coluna 2 (x=22): frota / reservas / locação / cobrança
    'GRUPO_VEICULO':   (22.0, 54.0),
    'VEICULO':         (22.0, 46.0),
    'PRONTUARIO':      (22.0, 38.0),
    'RESERVA':         (22.0, 30.0),
    'LOCACAO':         (22.0, 23.0),
    'VEICULO_PATIO':   (13.0, 16.0),
    'COBRANCA':        (22.0, 16.0),

    # Coluna 3 (x=38): acessórios / fotos / fila / proteções
    'FOTO':            (38.5, 54.0),
    'ACESSORIO':       (38.5, 46.0),
    'FILA_ESPERA':     (38.5, 30.0),
    'PROT_ADIC':       (38.5, 23.0),
}

# Rótulos alternativos para entidades com nomes longos (quebra de linha)
DISPLAYS = {
    'GRUPO_VEICULO': 'GRUPO\nVEICULO',
    'PRONTUARIO':    'PRONTUARIO\nVEICULO',
    'FILA_ESPERA':   'FILA\nESPERA',
    'PROT_ADIC':     'PROTECAO\nADICIONAL',
    'VEICULO_PATIO': 'VEICULO\nPATIO',
    'CLIENTE_PF':    'CLIENTE PF',
    'CLIENTE_PJ':    'CLIENTE PJ',
}

# Desenha todas as entidades iterando sobre o dicionário E
for name, (cx, cy) in E.items():
    draw_entity(ax, cx, cy, name, DISPLAYS.get(name))


# ══════════════════════════════════════════════════════════════════════════════
# ATRIBUTOS
# Cada tupla: (entidade, nome_atributo, é_pk, deslocamento_x, deslocamento_y)
# O deslocamento é relativo ao centro da entidade.
# Atributos são espalhados radialmente ao redor da entidade para não se sobreporem.
# ══════════════════════════════════════════════════════════════════════════════
ATTRS = [
    # EMPRESA — 4 atributos ao redor
    ('EMPRESA', 'id_empresa',   True,  -2.2,  2.4),   # PK: canto superior-esquerdo
    ('EMPRESA', 'cnpj',         False,  0.0,  2.6),   # topo
    ('EMPRESA', 'razao_social', False,  2.3,  2.2),   # canto superior-direito
    ('EMPRESA', 'ativo',        False,  2.5,  0.5),   # direita

    # GRUPO_VEICULO — 4 atributos
    ('GRUPO_VEICULO', 'id_grupo',         True,  -2.8,  2.4),
    ('GRUPO_VEICULO', 'codigo',           False,  0.0,  2.8),
    ('GRUPO_VEICULO', 'valor_diaria_base',False,  3.0,  2.2),
    ('GRUPO_VEICULO', 'descricao',        False,  3.2,  0.0),

    # FOTO — 3 atributos
    ('FOTO', 'id_foto', True,  -1.8,  2.4),
    ('FOTO', 'url',     False,  0.0,  2.6),
    ('FOTO', 'tipo',    False,  1.8,  2.2),

    # PATIO — 5 atributos (alguns abaixo para não colidir com relacionamentos)
    ('PATIO', 'id_patio',         True,  -2.4,  2.4),
    ('PATIO', 'nome',             False,  0.0,  2.6),
    ('PATIO', 'capacidade_total', False,  3.0,  2.0),
    ('PATIO', 'cidade',           False, -2.8, -2.0),  # abaixo-esquerda
    ('PATIO', 'estado',           False,  0.0, -2.5),  # abaixo

    # VEICULO — 8 atributos distribuídos em todas as direções
    ('VEICULO', 'id_veiculo',  True,  -2.2,  2.8),
    ('VEICULO', 'placa',       False,  0.0,  2.8),
    ('VEICULO', 'chassi',      False,  2.0,  2.8),
    ('VEICULO', 'marca',       False,  3.2,  1.5),
    ('VEICULO', 'modelo',      False,  3.4,  0.0),
    ('VEICULO', 'mecanizacao', False,  3.2, -1.5),
    ('VEICULO', 'status',      False,  0.5, -2.8),
    ('VEICULO', 'km_atual',    False, -2.0, -2.8),

    # ACESSORIO — 2 atributos (entidade simples)
    ('ACESSORIO', 'id_acessorio', True,  -2.5,  2.4),
    ('ACESSORIO', 'nome',         False,  0.5,  2.6),

    # VAGA — 3 atributos
    ('VAGA', 'id_vaga', True,  -2.0,  2.4),
    ('VAGA', 'codigo',  False,  0.0,  2.6),
    ('VAGA', 'status',  False,  2.0,  2.2),

    # PRONTUARIO — 4 atributos
    ('PRONTUARIO', 'id_registro',   True,  -2.8,  2.4),
    ('PRONTUARIO', 'data_registro', False,  0.0,  2.8),
    ('PRONTUARIO', 'tipo_registro', False,  3.2,  2.0),
    ('PRONTUARIO', 'km_atual',      False,  3.2, -2.0),

    # CLIENTE — 4 atributos (supertipo da hierarquia de herança)
    ('CLIENTE', 'id_cliente', True,  -2.2,  2.4),
    ('CLIENTE', 'email',      False,  0.0,  2.6),
    ('CLIENTE', 'tipo',       False, -2.8, -2.0),   # discriminador PF/PJ
    ('CLIENTE', 'cidade',     False,  0.0, -2.6),

    # RESERVA — 5 atributos
    ('RESERVA', 'id_reserva',     True,  -2.8,  2.4),
    ('RESERVA', 'data_reserva',   False,  0.0,  2.8),
    ('RESERVA', 'data_retirada',  False,  3.0,  2.2),
    ('RESERVA', 'status',         False,  3.5,  0.0),
    ('RESERVA', 'valor_estimado', False,  3.0, -2.0),

    # FILA_ESPERA — 3 atributos
    ('FILA_ESPERA', 'id_fila',      True,  -2.2,  2.4),
    ('FILA_ESPERA', 'data_desejada',False,  0.5,  2.7),
    ('FILA_ESPERA', 'duracao_dias', False,  2.8,  2.0),

    # CLIENTE_PF — 3 atributos (subtipo)
    ('CLIENTE_PF', 'cpf',             True,  -2.2,  2.4),
    ('CLIENTE_PF', 'nome',            False,  0.0,  2.6),
    ('CLIENTE_PF', 'data_nascimento', False,  2.5,  2.0),

    # CLIENTE_PJ — 2 atributos (subtipo)
    ('CLIENTE_PJ', 'cnpj',        True,  -2.0,  2.4),
    ('CLIENTE_PJ', 'razao_social',False,  0.5,  2.7),

    # CONDUTOR — 4 atributos
    ('CONDUTOR', 'id_condutor',    True,  -2.8,  2.4),
    ('CONDUTOR', 'num_cnh',        False,  0.0,  2.8),
    ('CONDUTOR', 'categoria_cnh',  False,  3.0,  2.0),
    ('CONDUTOR', 'data_exp_cnh',   False, -3.0, -2.0),

    # LOCACAO — 5 atributos (entidade central do sistema)
    ('LOCACAO', 'id_locacao',     True,  -2.8,  2.4),
    ('LOCACAO', 'data_retirada',  False,  0.0,  2.8),
    ('LOCACAO', 'data_devolucao', False,  3.2,  2.0),
    ('LOCACAO', 'status',         False,  3.5,  0.0),
    ('LOCACAO', 'km_saida',       False,  3.0, -2.0),

    # PROT_ADIC — 3 atributos
    ('PROT_ADIC', 'id_protecao',  True,  -2.8,  2.4),
    ('PROT_ADIC', 'nome',         False,  0.0,  2.7),
    ('PROT_ADIC', 'valor_diaria', False,  3.0,  2.0),

    # VEICULO_PATIO — 3 atributos (base para análise de Markov)
    ('VEICULO_PATIO', 'id_movimentacao', True,  -3.2,  2.4),
    ('VEICULO_PATIO', 'data_entrada',    False,  0.0,  2.8),
    ('VEICULO_PATIO', 'data_saida',      False,  3.0,  2.0),  # NULL = veículo ainda no pátio

    # COBRANCA — 4 atributos
    ('COBRANCA', 'id_cobranca', True,  -2.2,  2.4),
    ('COBRANCA', 'tipo',        False,  0.0,  2.6),   # INICIAL ou FINAL
    ('COBRANCA', 'valor_total', False,  2.5,  2.0),
    ('COBRANCA', 'status',      False,  2.5, -2.0),
]

# Itera a lista e chama draw_attr para cada atributo
for ent, lbl, pk, dx, dy in ATTRS:
    ex, ey = E[ent]                                   # posição da entidade-mãe
    draw_attr(ax, ex, ey, ex + dx, ey + dy, lbl, pk) # posição do atributo = centro + deslocamento


# ══════════════════════════════════════════════════════════════════════════════
# RELACIONAMENTOS
# Cada chamada posiciona um losango e o registra em REL_DIMS.
# As coordenadas foram escolhidas manualmente para evitar sobreposições.
# ══════════════════════════════════════════════════════════════════════════════

# ── Infraestrutura ────────────────────────────────────────────────────────────
draw_relationship(ax, 'possui',       6.0, 50.0, 'possui')         # EMPRESA → PATIO
draw_relationship(ax, 'proprietaria', 14.0, 50.0, 'proprietária')  # EMPRESA → VEICULO
draw_relationship(ax, 'contem',        6.0, 42.0, 'contém')        # PATIO → VAGA

# ── Frota ─────────────────────────────────────────────────────────────────────
draw_relationship(ax, 'classifica',  22.0, 50.0, 'classifica')     # GRUPO_VEICULO → VEICULO
draw_relationship(ax, 'tem',         30.5, 46.0, 'tem\n(N:M)')     # VEICULO ↔ ACESSORIO (muitos-para-muitos)
draw_relationship(ax, 'possui_foto', 30.5, 50.0, 'possui\nfoto')   # VEICULO → FOTO
draw_relationship(ax, 'possui_pron', 22.0, 42.0, 'possui\nprontuário') # VEICULO → PRONTUARIO

# ── Herança ISA (triângulos) ──────────────────────────────────────────────────
draw_isa(ax, 'isa_pf',  4.0, 26.5)   # CLIENTE é supertipo de CLIENTE_PF
draw_isa(ax, 'isa_pj',  9.2, 26.5)   # CLIENTE é supertipo de CLIENTE_PJ

# ── Condutores ────────────────────────────────────────────────────────────────
draw_relationship(ax, 'pode_ser',   3.2, 19.5, 'pode ser')  # CLIENTE_PF → CONDUTOR
draw_relationship(ax, 'autoriza',  10.0, 19.5, 'autoriza')  # CLIENTE_PJ → CONDUTOR

# ── Reservas ──────────────────────────────────────────────────────────────────
draw_relationship(ax, 'realiza',   14.0, 30.0, 'realiza')               # CLIENTE → RESERVA
draw_relationship(ax, 'solicitado',27.5, 40.5, 'solicitado\nem')         # GRUPO_VEICULO → RESERVA
draw_relationship(ax, 'ret_dev',   14.0, 37.0, 'retirada /\ndevolução')  # PATIO → RESERVA
draw_relationship(ax, 'entra_fila',29.0, 33.5, 'entra em\nfila')        # CLIENTE → FILA_ESPERA
draw_relationship(ax, 'aguardado', 33.0, 37.5, 'aguardado\nem')          # GRUPO_VEICULO → FILA_ESPERA

# ── Locação ───────────────────────────────────────────────────────────────────
draw_relationship(ax, 'origina',   22.0, 26.5, 'origina')         # RESERVA → LOCACAO (parcial: 0..1)
draw_relationship(ax, 'contrata',  14.0, 26.5, 'contrata')        # CLIENTE → LOCACAO
draw_relationship(ax, 'conduz',    14.0, 19.5, 'conduz')          # CONDUTOR → LOCACAO
draw_relationship(ax, 'alugado',   27.5, 34.5, 'alugado\nem')     # VEICULO → LOCACAO
draw_relationship(ax, 'saida_cheg',14.0, 34.5, 'saída /\nchegada')# PATIO → LOCACAO (saída e chegada)
draw_relationship(ax, 'documenta', 34.5, 37.5, 'documenta')       # LOCACAO → FOTO (fotos de inspeção)

# ── Proteção (N:M com atributo próprio) ──────────────────────────────────────
draw_relationship(ax, 'cont_prot', 30.5, 23.0, 'contrata\nprot. (N:M)')
# Atributo pendurado no relacionamento: valor negociado pode diferir da tabela
rel_attr(ax, 30.5, 23.0, 30.5, 20.0, 'valor_cobrado_diaria')

# ── Cobrança ──────────────────────────────────────────────────────────────────
draw_relationship(ax, 'gera',      22.0, 19.5, 'gera')            # LOCACAO → COBRANCA

# ── Rastreamento de pátio ─────────────────────────────────────────────────────
draw_relationship(ax, 'posicionado',17.5, 31.0, 'posicionado\nem')# VEICULO → VEICULO_PATIO
draw_relationship(ax, 'ocupa',      9.5,  27.0, 'ocupa')          # VAGA → VEICULO_PATIO
draw_relationship(ax, 'registra',  17.5, 19.5, 'registra')        # LOCACAO → VEICULO_PATIO


# ══════════════════════════════════════════════════════════════════════════════
# CONEXÕES RELACIONAMENTO ↔ ENTIDADE
# Cada par de chamadas link_rel_ent conecta as duas entidades que participam
# do relacionamento.  card= define a cardinalidade na ponta da entidade.
# dbl=True = linha dupla = participação total (toda instância da entidade
# participa de ao menos uma ocorrência do relacionamento).
# ══════════════════════════════════════════════════════════════════════════════

# possui: 1 EMPRESA possui N PÁTIOS (participação total de PATIO)
link_rel_ent(ax, 'possui',       'EMPRESA',       card='1')
link_rel_ent(ax, 'possui',       'PATIO',         card='N', dbl=True)

# proprietária: 1 EMPRESA proprietária de N VEÍCULOS
link_rel_ent(ax, 'proprietaria', 'EMPRESA',       card='1')
link_rel_ent(ax, 'proprietaria', 'VEICULO',       card='N', dbl=True)

# contém: 1 PATIO contém N VAGAS
link_rel_ent(ax, 'contem',       'PATIO',         card='1')
link_rel_ent(ax, 'contem',       'VAGA',          card='N', dbl=True)

# classifica: 1 GRUPO classifica N VEÍCULOS
link_rel_ent(ax, 'classifica',   'GRUPO_VEICULO', card='1')
link_rel_ent(ax, 'classifica',   'VEICULO',       card='N', dbl=True)

# tem: N VEÍCULOS têm M ACESSÓRIOS (N:M sem participação total obrigatória)
link_rel_ent(ax, 'tem',          'VEICULO',       card='N')
link_rel_ent(ax, 'tem',          'ACESSORIO',     card='M')

# possui foto: 1 VEÍCULO pode ter N FOTOS
link_rel_ent(ax, 'possui_foto',  'VEICULO',       card='1')
link_rel_ent(ax, 'possui_foto',  'FOTO',          card='N', dbl=True)

# possui prontuário: 1 VEÍCULO tem N registros de prontuário
link_rel_ent(ax, 'possui_pron',  'VEICULO',       card='1')
link_rel_ent(ax, 'possui_pron',  'PRONTUARIO',    card='N', dbl=True)

# ISA: sem cardinalidade (herança total/disjunta)
link_rel_ent(ax, 'isa_pf',  'CLIENTE',    card='')
link_rel_ent(ax, 'isa_pf',  'CLIENTE_PF', card='')
link_rel_ent(ax, 'isa_pj',  'CLIENTE',    card='')
link_rel_ent(ax, 'isa_pj',  'CLIENTE_PJ', card='')

# pode ser: 1 CLIENTE_PF pode ser N CONDUTORES registrados
link_rel_ent(ax, 'pode_ser', 'CLIENTE_PF', card='1')
link_rel_ent(ax, 'pode_ser', 'CONDUTOR',   card='N', dbl=True)

# autoriza: 1 CLIENTE_PJ autoriza N CONDUTORES (funcionários)
link_rel_ent(ax, 'autoriza', 'CLIENTE_PJ', card='1')
link_rel_ent(ax, 'autoriza', 'CONDUTOR',   card='N', dbl=True)

# realiza: 1 CLIENTE realiza N RESERVAS
link_rel_ent(ax, 'realiza',    'CLIENTE',       card='1')
link_rel_ent(ax, 'realiza',    'RESERVA',       card='N', dbl=True)

# solicitado em: 1 GRUPO é solicitado em N RESERVAS
link_rel_ent(ax, 'solicitado', 'GRUPO_VEICULO', card='1')
link_rel_ent(ax, 'solicitado', 'RESERVA',       card='N', dbl=True)

# retirada/devolução: 1 PATIO é usado em N RESERVAS
link_rel_ent(ax, 'ret_dev',    'PATIO',         card='1')
link_rel_ent(ax, 'ret_dev',    'RESERVA',       card='N', dbl=True)

# entra em fila: 1 CLIENTE entra em N posições na fila
link_rel_ent(ax, 'entra_fila', 'CLIENTE',       card='1')
link_rel_ent(ax, 'entra_fila', 'FILA_ESPERA',   card='N', dbl=True)

# aguardado em: 1 GRUPO aguardado em N posições da fila
link_rel_ent(ax, 'aguardado',  'GRUPO_VEICULO', card='1')
link_rel_ent(ax, 'aguardado',  'FILA_ESPERA',   card='N', dbl=True)

# origina: 1 RESERVA origina 0..1 LOCAÇÕES (nem toda reserva vira locação)
link_rel_ent(ax, 'origina',  'RESERVA', card='1')
link_rel_ent(ax, 'origina',  'LOCACAO', card='0..1', dbl=True)

# contrata: 1 CLIENTE contrata N LOCAÇÕES
link_rel_ent(ax, 'contrata', 'CLIENTE', card='1')
link_rel_ent(ax, 'contrata', 'LOCACAO', card='N', dbl=True)

# conduz: 1 CONDUTOR conduz em N LOCAÇÕES
link_rel_ent(ax, 'conduz',   'CONDUTOR', card='1')
link_rel_ent(ax, 'conduz',   'LOCACAO',  card='N', dbl=True)

# alugado em: 1 VEÍCULO alugado em N LOCAÇÕES (ao longo do tempo)
link_rel_ent(ax, 'alugado',    'VEICULO', card='1')
link_rel_ent(ax, 'alugado',    'LOCACAO', card='N', dbl=True)

# saída/chegada: 1 PATIO é ponto de saída/chegada em N LOCAÇÕES
link_rel_ent(ax, 'saida_cheg', 'PATIO',  card='1')
link_rel_ent(ax, 'saida_cheg', 'LOCACAO',card='N', dbl=True)

# documenta: 1 LOCACAO documentada em N FOTOS de entrega/devolução
link_rel_ent(ax, 'documenta',  'LOCACAO',card='1')
link_rel_ent(ax, 'documenta',  'FOTO',   card='N', dbl=True)

# contrata proteção: N LOCAÇÕES contratam M PROTEÇÕES (relacionamento N:M)
link_rel_ent(ax, 'cont_prot',  'LOCACAO',   card='N')
link_rel_ent(ax, 'cont_prot',  'PROT_ADIC', card='M')

# gera: 1 LOCACAO gera N COBRANÇAS (inicial + final)
link_rel_ent(ax, 'gera',       'LOCACAO',  card='1')
link_rel_ent(ax, 'gera',       'COBRANCA', card='N', dbl=True)

# posicionado em: 1 VEÍCULO tem N registros em VEICULO_PATIO (histórico)
link_rel_ent(ax, 'posicionado','VEICULO',       card='1')
link_rel_ent(ax, 'posicionado','VEICULO_PATIO', card='N', dbl=True)

# ocupa: 1 VAGA tem N entradas em VEICULO_PATIO (vários veículos ao longo do tempo)
link_rel_ent(ax, 'ocupa',      'VAGA',         card='1')
link_rel_ent(ax, 'ocupa',      'VEICULO_PATIO',card='N', dbl=True)

# registra: 1 LOCACAO registra N movimentações em VEICULO_PATIO
link_rel_ent(ax, 'registra',   'LOCACAO',      card='1')
link_rel_ent(ax, 'registra',   'VEICULO_PATIO',card='N', dbl=True)


# ══════════════════════════════════════════════════════════════════════════════
# LEGENDA
# Explica o significado visual de cada forma e convenção usada no diagrama.
# ══════════════════════════════════════════════════════════════════════════════
lx, ly = 0.3, 5.5                                         # posição da legenda (canto inferior esquerdo)
ax.text(lx, ly + 0.5, 'Legenda', fontsize=8, fontweight='bold', color='#374151')

# Lista de (cor_fundo, cor_borda, estilo, descrição)
items = [
    ('#BFDBFE', '#1D4ED8', 'solid', 'Entidade (retângulo)'),
    ('#FDE68A', '#B45309', 'solid', 'Relacionamento (losango)'),
    ('#BAE6FD', '#0369A1', 'solid', 'Herança ISA (triângulo)'),
    ('#DCFCE7', '#14532D', 'solid', 'Atributo PK (elipse sublinhada)'),
    ('#F0FFF4', '#15803D', 'solid', 'Atributo comum (elipse)'),
    ('#FEF9C3', '#A16207', 'solid', 'Atributo de relacionamento'),
]
for i, (fc, ec, ls, lbl) in enumerate(items):
    y = ly - 0.7 - i * 0.65                               # espaçamento vertical entre itens
    r = FancyBboxPatch((lx, y - 0.18), 0.55, 0.38,
                       boxstyle='square,pad=0.03',
                       facecolor=fc, edgecolor=ec, lw=1.2, zorder=6)
    ax.add_patch(r)
    ax.text(lx + 0.7, y + 0.01, lbl, fontsize=6.8, va='center',
            color='#374151', zorder=7)

# Notas de rodapé
ax.text(lx, ly - 5.3, '1 / N / M  =  cardinalidade (perto da entidade)',
        fontsize=6.5, color='#6B7280')
ax.text(lx, ly - 5.9, 'Linha dupla  =  participação total',
        fontsize=6.5, color='#6B7280')


# ══════════════════════════════════════════════════════════════════════════════
# EXPORTAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
out = '/Users/mei/dev/ufrj/big-data/docs/modelo_conceitual_chen.png'
plt.tight_layout(pad=0.4)                                 # ajusta margens automaticamente
plt.savefig(out, dpi=180, bbox_inches='tight',            # 180 dpi → boa qualidade para impressão
            facecolor=BG, edgecolor='none')
plt.close()                                               # libera memória
print(f'Saved: {out}')
