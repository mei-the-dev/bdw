# Notas do Projeto — Parte I
## MAE016 — 2026.1 | Grupo: [NOMES E DRE]

---

## O que foi feito

### Contexto

Modelamos o banco de dados relacional (OLTP) para o sistema transacional de uma das seis empresas do consórcio de locação de veículos. O escopo cobre os sistemas de cadastro de clientes, controle de frota, reservas, acompanhamento de locação, cobrança e controle de pátio — conforme especificado na avaliação.

---

### Entregas

#### 1. Modelo Conceitual (`docs/modelo_conceitual.md` + `docs/modelo_conceitual.png`)

Desenvolvido como Modelo Entidade-Relacionamento (MER). O diagrama cobre 20 entidades organizadas em cinco domínios funcionais:

- **Infraestrutura**: EMPRESA, PATIO, VAGA
- **Frota**: GRUPO_VEICULO, VEICULO, ACESSORIO, FOTO, PRONTUARIO_VEICULO
- **Clientes**: CLIENTE (supertipo), CLIENTE_PF, CLIENTE_PJ, CONDUTOR
- **Reservas**: RESERVA, FILA_ESPERA
- **Locação e Cobrança**: LOCACAO, PROTECAO_ADICIONAL, COBRANCA, VEICULO_PATIO

Decisões relevantes do modelo conceitual:

- **Herança de CLIENTE** via table-per-subtype: `cliente` concentra dados comuns; `cliente_pf` e `cliente_pj` estendem com PK = FK. Evita nulos excessivos sem abrir mão da integridade referencial.
- **CONDUTOR separado de CLIENTE**: o motorista pode ser o próprio cliente PF, um funcionário autorizado por um cliente PJ, ou um terceiro — as FKs opcionais suportam os três casos sem forçar um cadastro de cliente.
- **VEICULO_PATIO como entidade de histórico**: cada entrada e saída de vaga é um registro com timestamp. `data_saida IS NULL` indica presença atual. Esse histórico é a fonte direta para calcular a **matriz estocástica de Markov** exigida na análise de previsão de ocupação de pátio.
- **FOTO com FK opcional para LOCACAO**: fotos de propaganda têm `id_locacao = NULL`; fotos de entrega e devolução têm `id_locacao` preenchido. A constraint `chk_foto_tipo` faz essa regra valer em nível de banco.
- **COBRANÇA com tipo INICIAL/FINAL**: permite pré-cobrança na retirada (estimativa) e ajuste na devolução (real), sem duplicar entidades nem reabrir registros.
- **id_empresa em VEICULO**: necessário para os relatórios gerenciais de "origem" — distingue frota da empresa proprietária do pátio da frota das empresas associadas.

#### 2. Modelo Lógico (`docs/modelo_logico.md`)

Representação relacional de todas as 20 tabelas em notação formal, com:

- Chaves primárias e estrangeiras explicitadas
- Restrições de unicidade (UK)
- Restrições de domínio (CHECK)
- Cardinalidades de todos os relacionamentos

O modelo está na **Terceira Forma Normal (3FN)**: sem grupos repetidos, sem dependências parciais de chave, sem dependências transitivas.

#### 3. Dicionário de Dados (`docs/dicionario_dados.md`)

Documentação coluna a coluna de todas as 20 tabelas, incluindo:

- Tipo de dado, nulabilidade e valor padrão
- Descrição semântica de cada atributo
- Todas as restrições de integridade (PK, FK, UK, CHECK)
- Tabela consolidada de restrições ao final
- Definição dos 13 tipos enumerados utilizados

#### 4. Modelo Físico (`sql/ddl.sql`)

Script SQL/DDL compatível com **ANSI SQL:2003 / PostgreSQL 15+**, contendo:

- `CREATE SCHEMA locadora`
- 13 tipos enumerados (`CREATE TYPE ... AS ENUM`)
- 20 tabelas com todas as constraints
- FK de `foto → locacao` adicionada via `ALTER TABLE` (dependência circular resolvida)
- 17 índices para suporte às queries dos relatórios gerenciais e da análise de Markov
- `COMMENT ON TABLE` para autodocumentação no banco

---

### Cobertura dos Relatórios Gerenciais

| Relatório | Tabelas principais |
|---|---|
| Controle de pátio (veículos por grupo e origem) | `veiculo_patio`, `vaga`, `patio`, `veiculo`, `empresa` |
| Controle de locações ativas (grupo + tempo restante) | `locacao`, `veiculo`, `grupo_veiculo` |
| Controle de reservas (grupo, pátio, tempo, cidade) | `reserva`, `grupo_veiculo`, `patio`, `cliente` |
| Grupos mais alugados por origem do cliente | `locacao`, `veiculo`, `grupo_veiculo`, `cliente`, `cliente_pf/pj` |
| Matriz de Markov (% movimentação entre pátios) | `veiculo_patio`, `vaga`, `patio`, `locacao` |

---

### Arquivos Gerados

```
.
├── README.md
├── sql/
│   └── ddl.sql
└── docs/
    ├── modelo_conceitual.md
    ├── modelo_conceitual.png
    ├── modelo_logico.md
    ├── dicionario_dados.md
    ├── notas_projeto.md        ← este arquivo
    └── gerar_er.py             (script que gerou o PNG)
```
