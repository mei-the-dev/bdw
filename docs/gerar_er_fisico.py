#!/usr/bin/env python3
"""
gerar_er_fisico.py — Physical/relational schema ER diagram
Renders all 20 tables from sql/ddl.sql as a PNG schema diagram:
  • columns with PK / FK colour coding
  • FK arrows from source column to target PK column
Output: docs/modelo_fisico_er.png
"""

import os
import matplotlib
matplotlib.use('Agg')           # headless backend — no display required
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ── visual constants ─────────────────────────────────────────────────────────
ROW_H  = 0.36   # height of each column row in axis units
HDR_H  = 0.60   # height of the table header bar
TBL_W  = 5.20   # width of every table box

# Colour palette — all UI colours in one place for easy tweaking
C = {
    'hdr':       '#1e3a5f',  # table header background — dark navy
    'hdr_txt':   '#ffffff',  # table header text — white
    'pk':        '#fff3cd',  # PK-only row — amber tint
    'fk':        '#d1ecf1',  # FK-only row — cyan tint
    'pkfk':      '#d4edda',  # PK+FK row   — green tint
    'row_a':     '#f8f9fa',  # normal row (even index)  — near white
    'row_b':     '#eef0f2',  # normal row (odd index)   — light gray
    'border':    '#495057',  # box / row border
    'arrow':     '#c0392b',  # FK arrow line — dark red
    'pk_mark':   '#856404',  # 'PK' label text — dark amber
    'fk_mark':   '#0c5460',  # 'FK' label text — dark teal
    'pkfk_mark': '#155724',  # 'PK·FK' label text — dark green
    'dot_mark':  '#adb5bd',  # '·' placeholder — gray
    'text':      '#212529',  # normal column name text — near black
    'type_txt':  '#6c757d',  # data-type label — medium gray
    'bg':        '#f0f2f5',  # figure background — very light gray
    'section':   '#495057',  # section label text
}

# ── table definitions ────────────────────────────────────────────────────────
# Each tuple: (table_name, [(col_name, type_str, is_pk, fk_ref), ...])
# fk_ref  — target table name string, or None
TABLES = [
    ('empresa', [
        ('id_empresa',    'serial',    True,  None),
        ('cnpj',          'chr(14)',   False, None),
        ('razao_social',  'str(200)',  False, None),
        ('nome_fantasia', 'str(200)',  False, None),
        ('email',         'str(150)',  False, None),
        ('telefone',      'str(20)',   False, None),
        ('ativo',         'bool',      False, None),
        ('criado_em',     'ts',        False, None),
    ]),
    ('patio', [
        ('id_patio',         'serial',   True,  None),
        ('id_empresa',       'int',      False, 'empresa'),
        ('nome',             'str(150)', False, None),
        ('logradouro',       'str(200)', False, None),
        ('numero',           'str(10)',  False, None),
        ('complemento',      'str(100)', False, None),
        ('bairro',           'str(100)', False, None),
        ('cidade',           'str(100)', False, None),
        ('estado',           'chr(2)',   False, None),
        ('cep',              'chr(8)',   False, None),
        ('capacidade_total', 'int',      False, None),
        ('ativo',            'bool',     False, None),
    ]),
    ('vaga', [
        ('id_vaga',  'serial',  True,  None),
        ('id_patio', 'int',     False, 'patio'),
        ('codigo',   'str(10)', False, None),
        ('status',   'enum',    False, None),
    ]),
    ('grupo_veiculo', [
        ('id_grupo',           'serial',   True,  None),
        ('codigo',             'str(10)',  False, None),
        ('descricao',          'str(200)', False, None),
        ('valor_diaria_base',  'num',      False, None),
        ('descricao_luxo',     'str(500)', False, None),
        ('ativo',              'bool',     False, None),
    ]),
    ('veiculo', [
        ('id_veiculo',        'serial',   True,  None),
        ('id_grupo',          'int',      False, 'grupo_veiculo'),
        ('id_empresa',        'int',      False, 'empresa'),
        ('placa',             'str(8)',   False, None),
        ('chassi',            'str(17)',  False, None),
        ('marca',             'str(50)',  False, None),
        ('modelo',            'str(100)', False, None),
        ('versao',            'str(100)', False, None),
        ('cor',               'str(50)',  False, None),
        ('ano_fabricacao',    'sint',     False, None),
        ('ano_modelo',        'sint',     False, None),
        ('ar_condicionado',   'bool',     False, None),
        ('mecanizacao',       'enum',     False, None),
        ('tem_cadeirinha',    'bool',     False, None),
        ('tem_bebe_conforto', 'bool',     False, None),
        ('num_portas',        'sint',     False, None),
        ('capacidade_pass',   'sint',     False, None),
        ('combustivel',       'str(30)',  False, None),
        ('status',            'enum',     False, None),
        ('km_atual',          'num',      False, None),
        ('criado_em',         'ts',       False, None),
    ]),
    ('acessorio', [
        ('id_acessorio', 'serial',   True,  None),
        ('nome',         'str(100)', False, None),
        ('descricao',    'str(300)', False, None),
    ]),
    ('veiculo_acessorio', [
        ('id_veiculo',   'int', True, 'veiculo'),
        ('id_acessorio', 'int', True, 'acessorio'),
    ]),
    ('foto', [
        ('id_foto',    'serial',   True,  None),
        ('id_veiculo', 'int',      False, 'veiculo'),
        ('id_locacao', 'int',      False, 'locacao'),
        ('url',        'str(500)', False, None),
        ('tipo',       'enum',     False, None),
        ('data_foto',  'ts',       False, None),
        ('descricao',  'str(300)', False, None),
    ]),
    ('prontuario_veiculo', [
        ('id_registro',        'serial',   True,  None),
        ('id_veiculo',         'int',      False, 'veiculo'),
        ('data_registro',      'ts',       False, None),
        ('tipo_registro',      'enum',     False, None),
        ('descricao',          'text',     False, None),
        ('km_atual',           'num',      False, None),
        ('nivel_oleo',         'enum',     False, None),
        ('pressao_pneu_dd',    'num',      False, None),
        ('pressao_pneu_de',    'num',      False, None),
        ('pressao_pneu_td',    'num',      False, None),
        ('pressao_pneu_te',    'num',      False, None),
        ('proxima_revisao_km', 'num',      False, None),
        ('responsavel',        'str(150)', False, None),
    ]),
    ('cliente', [
        ('id_cliente',    'serial',   True,  None),
        ('tipo',          'enum',     False, None),
        ('email',         'str(150)', False, None),
        ('telefone',      'str(20)',  False, None),
        ('logradouro',    'str(200)', False, None),
        ('numero',        'str(10)',  False, None),
        ('complemento',   'str(100)', False, None),
        ('bairro',        'str(100)', False, None),
        ('cidade',        'str(100)', False, None),
        ('estado',        'chr(2)',   False, None),
        ('cep',           'chr(8)',   False, None),
        ('data_cadastro', 'ts',       False, None),
        ('ativo',         'bool',     False, None),
    ]),
    ('cliente_pf', [
        ('id_cliente',      'int',      True, 'cliente'),
        ('cpf',             'chr(11)',  False, None),
        ('nome',            'str(100)', False, None),
        ('sobrenome',       'str(100)', False, None),
        ('data_nascimento', 'date',     False, None),
        ('rg',              'str(20)',  False, None),
    ]),
    ('cliente_pj', [
        ('id_cliente',         'int',      True, 'cliente'),
        ('cnpj',               'chr(14)',  False, None),
        ('razao_social',       'str(200)', False, None),
        ('nome_fantasia',      'str(200)', False, None),
        ('inscricao_estadual', 'str(30)',  False, None),
    ]),
    ('condutor', [
        ('id_condutor',        'serial',   True,  None),
        ('id_cliente_pf',      'int',      False, 'cliente_pf'),
        ('id_cliente_pj',      'int',      False, 'cliente_pj'),
        ('nome',               'str(200)', False, None),
        ('cpf',                'chr(11)',  False, None),
        ('num_cnh',            'str(20)',  False, None),
        ('categoria_cnh',      'enum',     False, None),
        ('data_expiracao_cnh', 'date',     False, None),
        ('data_nascimento',    'date',     False, None),
        ('ativo',              'bool',     False, None),
    ]),
    ('reserva', [
        ('id_reserva',              'serial', True,  None),
        ('id_cliente',              'int',    False, 'cliente'),
        ('id_grupo',                'int',    False, 'grupo_veiculo'),
        ('id_veiculo',              'int',    False, 'veiculo'),
        ('id_patio_retirada',       'int',    False, 'patio'),
        ('id_patio_devolucao',      'int',    False, 'patio'),
        ('data_reserva',            'ts',     False, None),
        ('data_prev_retirada',      'ts',     False, None),
        ('data_prev_devolucao',     'ts',     False, None),
        ('status',                  'enum',   False, None),
        ('valor_estimado',          'num',    False, None),
        ('observacoes',             'text',   False, None),
    ]),
    ('fila_espera', [
        ('id_fila',           'serial', True,  None),
        ('id_cliente',        'int',    False, 'cliente'),
        ('id_grupo',          'int',    False, 'grupo_veiculo'),
        ('id_patio_retirada', 'int',    False, 'patio'),
        ('data_solicitacao',  'ts',     False, None),
        ('data_desejada',     'ts',     False, None),
        ('duracao_dias',      'sint',   False, None),
        ('ativo',             'bool',   False, None),
        ('observacoes',       'text',   False, None),
    ]),
    ('locacao', [
        ('id_locacao',               'serial', True,  None),
        ('id_reserva',               'int',    False, 'reserva'),
        ('id_cliente',               'int',    False, 'cliente'),
        ('id_condutor',              'int',    False, 'condutor'),
        ('id_veiculo',               'int',    False, 'veiculo'),
        ('id_patio_saida',           'int',    False, 'patio'),
        ('id_patio_chegada',         'int',    False, 'patio'),
        ('dh_prev_retirada',         'ts',     False, None),
        ('dh_retirada',              'ts',     False, None),
        ('dh_prev_devolucao',        'ts',     False, None),
        ('dh_devolucao',             'ts',     False, None),
        ('km_saida',                 'num',    False, None),
        ('km_chegada',               'num',    False, None),
        ('status',                   'enum',   False, None),
        ('obs_entrega',              'text',   False, None),
        ('obs_devolucao',            'text',   False, None),
        ('criado_em',                'ts',     False, None),
    ]),
    ('protecao_adicional', [
        ('id_protecao',            'serial',   True,  None),
        ('nome',                   'str(100)', False, None),
        ('descricao',              'text',     False, None),
        ('valor_adicional_diaria', 'num',      False, None),
        ('ativo',                  'bool',     False, None),
    ]),
    ('locacao_protecao', [
        ('id_locacao',           'int', True, 'locacao'),
        ('id_protecao',          'int', True, 'protecao_adicional'),
        ('valor_cobrado_diaria', 'num', False, None),
    ]),
    ('cobranca', [
        ('id_cobranca',        'serial', True,  None),
        ('id_locacao',         'int',    False, 'locacao'),
        ('tipo',               'enum',   False, None),
        ('data_emissao',       'ts',     False, None),
        ('data_vencimento',    'date',   False, None),
        ('data_pagamento',     'ts',     False, None),
        ('num_diarias',        'num',    False, None),
        ('valor_diaria',       'num',    False, None),
        ('valor_protecoes',    'num',    False, None),
        ('valor_km_excedente', 'num',    False, None),
        ('valor_outros',       'num',    False, None),
        ('valor_total',        'num',    False, None),
        ('status',             'enum',   False, None),
        ('forma_pagamento',    'enum',   False, None),
        ('num_transacao',      'str(100)', False, None),
        ('observacoes',        'text',   False, None),
    ]),
    ('veiculo_patio', [
        ('id_movimentacao', 'serial', True,  None),
        ('id_veiculo',      'int',    False, 'veiculo'),
        ('id_vaga',         'int',    False, 'vaga'),
        ('id_locacao',      'int',    False, 'locacao'),
        ('data_entrada',    'ts',     False, None),
        ('data_saida',      'ts',     False, None),
    ]),
]

# Fast lookup dict: table_name → list of column tuples
TABLES_DICT = dict(TABLES)

# ── layout ───────────────────────────────────────────────────────────────────
# 7 columns; tables listed top-to-bottom within each column.
COLUMN_ORDER = [
    ['empresa', 'acessorio', 'protecao_adicional'],       # col 0 — shared master data
    ['patio', 'vaga', 'grupo_veiculo'],                    # col 1 — locations + categories
    ['veiculo', 'veiculo_acessorio'],                      # col 2 — vehicle core
    ['foto', 'prontuario_veiculo', 'veiculo_patio'],       # col 3 — vehicle documents
    ['cliente', 'cliente_pf', 'cliente_pj', 'condutor'],  # col 4 — people
    ['reserva', 'fila_espera'],                            # col 5 — reservations
    ['locacao', 'locacao_protecao', 'cobranca'],           # col 6 — active contracts
]

# Horizontal centre of each column (7 cols, step = 6 units)
COL_X   = [3.0, 9.0, 15.0, 21.0, 27.0, 33.0, 39.0]
START_Y = 19.5   # top edge of the first table in every column
GAP_Y   = 0.80   # vertical gap between stacked tables


def _compute_layout() -> dict:
    """Return {table_name: (center_x, top_y)} for every table."""
    layout = {}
    for col_idx, col_tables in enumerate(COLUMN_ORDER):
        cx    = COL_X[col_idx]
        cur_y = START_Y
        for tname in col_tables:
            layout[tname] = (cx, cur_y)
            # Advance cursor downward past this table plus the gap
            n_rows = len(TABLES_DICT[tname])
            cur_y -= HDR_H + n_rows * ROW_H + GAP_Y
    return layout


LAYOUT = _compute_layout()


# ── geometry helpers ─────────────────────────────────────────────────────────

def _row_center_y(table: str, col_name: str) -> float:
    """Y-coordinate of the vertical centre of the row for col_name in table."""
    _, top_y = LAYOUT[table]
    for i, (cn, *_rest) in enumerate(TABLES_DICT[table]):
        if cn == col_name:
            row_bottom = top_y - HDR_H - (i + 1) * ROW_H
            return row_bottom + ROW_H / 2   # centre of this row
    return top_y - HDR_H / 2               # fallback: header centre


def _pk_row_y(table: str) -> float:
    """Y-coordinate of the first PK column row in table."""
    for cn, _t, is_pk, _fk in TABLES_DICT[table]:
        if is_pk:
            return _row_center_y(table, cn)
    return LAYOUT[table][1] - HDR_H / 2    # fallback


def _left(name: str)  -> float: return LAYOUT[name][0] - TBL_W / 2
def _right(name: str) -> float: return LAYOUT[name][0] + TBL_W / 2


# ── drawing: table box ───────────────────────────────────────────────────────

def draw_table(ax, name: str) -> None:
    """Render one table as a labelled box with coloured column rows."""
    cols      = TABLES_DICT[name]
    cx, top_y = LAYOUT[name]
    left      = cx - TBL_W / 2

    # Header bar
    ax.add_patch(patches.Rectangle(
        (left, top_y - HDR_H), TBL_W, HDR_H,
        facecolor=C['hdr'], edgecolor='none', zorder=2
    ))
    ax.text(cx, top_y - HDR_H / 2, name,
            ha='center', va='center',
            color=C['hdr_txt'], fontsize=7, fontweight='bold',
            fontfamily='monospace', zorder=3)

    # Column rows
    for i, (col_name, col_type, is_pk, fk_ref) in enumerate(cols):
        row_bottom = top_y - HDR_H - (i + 1) * ROW_H

        # Choose row background by key type
        if is_pk and fk_ref:
            bg = C['pkfk']
        elif is_pk:
            bg = C['pk']
        elif fk_ref:
            bg = C['fk']
        else:
            bg = C['row_a'] if i % 2 == 0 else C['row_b']

        ax.add_patch(patches.Rectangle(
            (left, row_bottom), TBL_W, ROW_H,
            facecolor=bg, edgecolor='none', zorder=2
        ))
        # Thin horizontal separator between rows
        ax.plot([left, left + TBL_W], [row_bottom + ROW_H] * 2,
                color=C['border'], lw=0.25, zorder=3)

        row_cy = row_bottom + ROW_H / 2

        # Key-type marker (left margin)
        if is_pk and fk_ref:
            marker, mc = 'PK·FK', C['pkfk_mark']
        elif is_pk:
            marker, mc = ' PK ', C['pk_mark']
        elif fk_ref:
            marker, mc = ' FK ', C['fk_mark']
        else:
            marker, mc = '  · ', C['dot_mark']

        ax.text(left + 0.08, row_cy, marker,
                ha='left', va='center', fontsize=5, fontweight='bold',
                color=mc, fontfamily='monospace', zorder=4)

        # Column name (bold for key columns)
        ax.text(left + 0.75, row_cy, col_name,
                ha='left', va='center', fontsize=5.5,
                color=C['text'],
                fontweight='bold' if (is_pk or fk_ref) else 'normal',
                fontfamily='monospace', zorder=4)

        # Data type (right-aligned, muted)
        ax.text(left + TBL_W - 0.08, row_cy, col_type,
                ha='right', va='center', fontsize=5,
                color=C['type_txt'], fontfamily='monospace', zorder=4)

    # Outer border drawn last so it sits on top of all row fills
    total_h = HDR_H + len(cols) * ROW_H
    ax.add_patch(patches.FancyBboxPatch(
        (left, top_y - total_h), TBL_W, total_h,
        boxstyle='square,pad=0',
        facecolor='none', edgecolor=C['border'], lw=0.9, zorder=5
    ))


# ── drawing: FK arrows ───────────────────────────────────────────────────────

def draw_fk_arrows(ax) -> None:
    """Draw one annotate arrow per FK column, from source row to target PK row."""
    for tname, cols in TABLES:
        src_cx = LAYOUT[tname][0]
        for col_name, _t, _pk, fk_ref in cols:
            if not fk_ref or fk_ref not in LAYOUT:
                continue    # not a FK, or references a table not in our diagram

            tgt_cx = LAYOUT[fk_ref][0]
            src_y  = _row_center_y(tname, col_name)
            tgt_y  = _pk_row_y(fk_ref)

            same_col = abs(tgt_cx - src_cx) < 0.5

            if same_col:
                # Loop arrow on the left side for within-column FK references
                sx, tx, rad = _left(tname), _left(fk_ref), -0.5
            elif tgt_cx > src_cx:
                # Target is to the right — exit from right, enter from left
                sx, tx, rad = _right(tname), _left(fk_ref), 0.12
            else:
                # Target is to the left — exit from left, enter from right
                sx, tx, rad = _left(tname), _right(fk_ref), -0.12

            ax.annotate(
                '',
                xy=(tx, tgt_y),         # arrowhead lands on target PK row
                xytext=(sx, src_y),     # tail starts at source FK row
                zorder=1,
                arrowprops=dict(
                    arrowstyle='-|>',
                    color=C['arrow'],
                    lw=0.55,
                    alpha=0.55,
                    mutation_scale=5,
                    connectionstyle=f'arc3,rad={rad}',
                )
            )


# ── section labels ────────────────────────────────────────────────────────────

SECTIONS = [
    (COL_X[0], 'Infraestrutura'),
    (COL_X[1], 'Localização'),
    (COL_X[2], 'Frota'),
    (COL_X[3], 'Docs Frota'),
    (COL_X[4], 'Clientes'),
    (COL_X[5], 'Reservas'),
    (COL_X[6], 'Locação / Cobr.'),
]


# ── legend ────────────────────────────────────────────────────────────────────

def draw_legend(ax) -> None:
    """Render a small colour-key legend in the bottom-left corner."""
    items = [
        (C['pk'],   ' PK      — Primary Key'),
        (C['fk'],   ' FK      — Foreign Key'),
        (C['pkfk'], ' PK·FK   — PK + FK'),
    ]
    lx, ly   = 0.3, 0.4
    lw       = 4.8
    row_h    = 0.38
    pad      = 0.25
    box_h    = pad + len(items) * row_h + 0.1

    ax.add_patch(patches.Rectangle(
        (lx, ly), lw, box_h,
        facecolor='white', edgecolor=C['border'], lw=0.6, zorder=8
    ))
    for j, (bg, label) in enumerate(items):
        ey = ly + box_h - pad - j * row_h
        ax.add_patch(patches.Rectangle(
            (lx + 0.15, ey - 0.12), 0.28, 0.24,
            facecolor=bg, edgecolor=C['border'], lw=0.4, zorder=9
        ))
        ax.text(lx + 0.55, ey, label,
                ha='left', va='center', fontsize=5.5,
                fontfamily='monospace', zorder=9)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    FIG_W, FIG_H = 43.5, 21.5

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(C['bg'])
    ax.set_facecolor(C['bg'])
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(0, FIG_H)
    ax.set_aspect('equal')
    ax.axis('off')

    # Title
    ax.text(FIG_W / 2, FIG_H - 0.50,
            'Modelo Físico — Locadora de Veículos — MAE016 UFRJ 2026.1',
            ha='center', va='center', fontsize=10, fontweight='bold',
            color=C['hdr'])

    # Section labels (one per column)
    for sx, slabel in SECTIONS:
        ax.text(sx, START_Y + 0.90, slabel,
                ha='center', va='center', fontsize=6.2,
                color=C['section'], fontstyle='italic')

    # FK arrows drawn first so table boxes render on top
    draw_fk_arrows(ax)

    # Table boxes
    for name, _ in TABLES:
        draw_table(ax, name)

    # Legend
    draw_legend(ax)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modelo_fisico_er.png')
    fig.savefig(out, dpi=100, bbox_inches='tight',
                facecolor=C['bg'], edgecolor='none')
    plt.close(fig)
    print(f'Saved: {out}')


if __name__ == '__main__':
    main()
