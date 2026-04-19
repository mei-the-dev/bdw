# Avaliação 01 — Modelagem de Data Warehouse
## MAE016 — Bancos de Dados e Big Data | UFRJ / NCE — 2026.1

**Grupo:**
| Nome Completo | DRE |
|---|---|
| [NOME 1] | [DRE 1] |
| [NOME 2] | [DRE 2] |
| [NOME 3] | [DRE 3] |
| [NOME 4] | [DRE 4] |

---

## PARTE I — Modelagem SBD OLTP

Projeto do Banco de Dados Relacional para o sistema transacional de uma das empresas do consórcio de locação de veículos.

### Contexto

Seis empresas independentes de locação associaram-se para compartilhar pátios (Galeão, Santos Dumont, Rodoviária, Rio Sul, Nova América, Barra Shopping). Cada empresa mantém seu sistema operativo próprio. A modificação é mínima: o sistema de reserva/locação passa a permitir retirada e devolução em qualquer dos seis pátios.

O escopo modelado cobre:
- Cadastro de clientes (PF e PJ) e condutores
- Controle da frota de veículos
- Sistema de reservas e fila de espera
- Acompanhamento da locação (retirada, devolução, KM)
- Cobrança (estimativa inicial e ajuste final)
- Controle de pátio e histórico de movimentações

---

## Estrutura do Repositório

```
.
├── README.md
├── sql/
│   └── ddl.sql          # Modelo Físico — SQL DDL (ANSI SQL:2003 / PostgreSQL 15+)
└── docs/
    ├── modelo_conceitual.md   # Modelo Conceitual (MER via Mermaid erDiagram)
    ├── modelo_logico.md       # Modelo Lógico (notação relacional + cardinalidades)
    └── dicionario_dados.md    # Dicionário de Dados + Restrições de Integridade
```

---

## Entidades Modeladas

| # | Entidade | Sistema |
|---|---|---|
| 1 | `empresa` | Cadastro |
| 2 | `patio` | Controle de Pátio |
| 3 | `vaga` | Controle de Pátio |
| 4 | `grupo_veiculo` | Frota |
| 5 | `veiculo` | Frota |
| 6 | `acessorio` | Frota |
| 7 | `veiculo_acessorio` | Frota |
| 8 | `foto` | Frota / Locação |
| 9 | `prontuario_veiculo` | Frota |
| 10 | `cliente` | Cadastro de Clientes |
| 11 | `cliente_pf` | Cadastro de Clientes |
| 12 | `cliente_pj` | Cadastro de Clientes |
| 13 | `condutor` | Cadastro / Locação |
| 14 | `reserva` | Sistema de Reserva |
| 15 | `fila_espera` | Sistema de Reserva |
| 16 | `locacao` | Acompanhamento de Locação |
| 17 | `protecao_adicional` | Cobrança |
| 18 | `locacao_protecao` | Cobrança |
| 19 | `cobranca` | Sistema de Cobrança |
| 20 | `veiculo_patio` | Controle de Pátio / Análise Markov |

---

## Como Executar o DDL

```bash
# PostgreSQL
psql -U postgres -f sql/ddl.sql

# ou dentro do psql
\i sql/ddl.sql
```

---

## Decisões de Projeto Relevantes

1. **Herança de CLIENTE** (table-per-subtype): `cliente` guarda dados comuns; `cliente_pf` e `cliente_pj` estendem via PK = FK.

2. **CONDUTOR desacoplado de CLIENTE**: suporta três casos — cliente PF como motorista, funcionário de PJ, ou terceiro autorizado.

3. **VEICULO com id_empresa**: necessário para relatórios gerenciais de "origem" do veículo no pátio (frota própria vs. frota de associadas).

4. **COBRANÇA com tipo INICIAL/FINAL**: permite pré-cobrança na retirada e ajuste na devolução sem reabrir registros.

5. **VEICULO_PATIO como histórico completo**: cada entrada/saída de vaga é um registro. `data_saida IS NULL` indica presença atual. Esse histórico é a fonte direta para a **matriz estocástica de Markov** (percentual de veículos entregues em cada pátio por pátio de origem).

6. **RESERVA com pátio de retirada e devolução independentes**: reflete a nova capacidade do consórcio (one-way rental).
