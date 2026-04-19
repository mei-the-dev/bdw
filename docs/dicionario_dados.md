# Dicionário de Dados — Locadora de Veículos
## MAE016 — 2026.1 | Grupo: [NOMES E DRE]

Schema: `locadora` | SGBD: PostgreSQL 15+ | Padrão: ANSI SQL:2003

---

## Tipos Enumerados

| Tipo | Valores |
|---|---|
| `tipo_cliente_enum` | `PF`, `PJ` |
| `status_veiculo_enum` | `DISPONIVEL`, `ALUGADO`, `MANUTENCAO`, `INATIVO` |
| `tipo_mecanizacao_enum` | `MANUAL`, `AUTOMATICA` |
| `status_vaga_enum` | `LIVRE`, `OCUPADA`, `RESERVADA`, `MANUTENCAO` |
| `tipo_foto_enum` | `PROPAGANDA`, `ENTREGA`, `DEVOLUCAO` |
| `tipo_registro_enum` | `REVISAO`, `INSPECAO`, `MANUTENCAO_CORRETIVA`, `MANUTENCAO_PREVENTIVA` |
| `nivel_fluido_enum` | `OK`, `BAIXO`, `CRITICO` |
| `categoria_cnh_enum` | `A`, `B`, `C`, `D`, `E`, `AB`, `AC`, `AD`, `AE` |
| `status_reserva_enum` | `CONFIRMADA`, `CANCELADA`, `EM_ESPERA`, `CONCLUIDA`, `EXPIRADA` |
| `status_locacao_enum` | `ATIVA`, `CONCLUIDA`, `CANCELADA` |
| `tipo_cobranca_enum` | `INICIAL`, `FINAL`, `ADICIONAL` |
| `status_cobranca_enum` | `PENDENTE`, `PAGO`, `CANCELADO`, `ATRASADO` |
| `forma_pagamento_enum` | `CARTAO_CREDITO`, `CARTAO_DEBITO`, `PIX`, `BOLETO`, `DINHEIRO` |

---

## Tabelas

---

### empresa

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_empresa` | SERIAL | NÃO | auto | PK | Identificador da empresa |
| `cnpj` | CHAR(14) | NÃO | — | UK | CNPJ sem formatação |
| `razao_social` | VARCHAR(200) | NÃO | — | — | Razão social |
| `nome_fantasia` | VARCHAR(200) | SIM | — | — | Nome fantasia |
| `email` | VARCHAR(150) | SIM | — | — | E-mail de contato |
| `telefone` | VARCHAR(20) | SIM | — | — | Telefone de contato |
| `ativo` | BOOLEAN | NÃO | TRUE | — | Indica se a empresa está ativa |
| `criado_em` | TIMESTAMP | NÃO | NOW() | — | Data de cadastro |

---

### patio

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_patio` | SERIAL | NÃO | auto | PK | Identificador do pátio |
| `id_empresa` | INTEGER | NÃO | — | FK empresa | Empresa proprietária do pátio |
| `nome` | VARCHAR(150) | NÃO | — | — | Nome descritivo (ex: "Pátio Galeão") |
| `logradouro` | VARCHAR(200) | NÃO | — | — | Rua/avenida |
| `numero` | VARCHAR(10) | SIM | — | — | Número |
| `complemento` | VARCHAR(100) | SIM | — | — | Complemento |
| `bairro` | VARCHAR(100) | SIM | — | — | Bairro |
| `cidade` | VARCHAR(100) | NÃO | — | — | Cidade |
| `estado` | CHAR(2) | NÃO | — | — | UF (ex: RJ) |
| `cep` | CHAR(8) | NÃO | — | — | CEP sem hífen |
| `capacidade_total` | INTEGER | NÃO | — | > 0 | Total de vagas do pátio |
| `ativo` | BOOLEAN | NÃO | TRUE | — | Indica se o pátio está operacional |

---

### vaga

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_vaga` | SERIAL | NÃO | auto | PK | Identificador da vaga |
| `id_patio` | INTEGER | NÃO | — | FK patio | Pátio ao qual a vaga pertence |
| `codigo` | VARCHAR(10) | NÃO | — | UK(patio) | Código alfanumérico único no pátio |
| `status` | status_vaga_enum | NÃO | `LIVRE` | — | Estado atual da vaga |

**Restrição de unicidade:** `(id_patio, codigo)` — mesmo código pode existir em pátios distintos.

---

### grupo_veiculo

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_grupo` | SERIAL | NÃO | auto | PK | Identificador do grupo |
| `codigo` | VARCHAR(10) | NÃO | — | UK | Código curto (ex: A, B, SUV) |
| `descricao` | VARCHAR(200) | NÃO | — | — | Descrição do grupo |
| `valor_diaria_base` | NUMERIC(10,2) | NÃO | — | > 0 | Valor base da diária em R$ |
| `descricao_luxo` | VARCHAR(500) | SIM | — | — | Texto descritivo para o cliente |
| `ativo` | BOOLEAN | NÃO | TRUE | — | Grupo disponível para reserva |

---

### veiculo

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_veiculo` | SERIAL | NÃO | auto | PK | Identificador do veículo |
| `id_grupo` | INTEGER | NÃO | — | FK grupo_veiculo | Grupo/categoria do veículo |
| `id_empresa` | INTEGER | NÃO | — | FK empresa | Empresa proprietária |
| `placa` | VARCHAR(8) | NÃO | — | UK | Placa (padrão Mercosul ou antigo) |
| `chassi` | VARCHAR(17) | NÃO | — | UK | Número de chassi (VIN) |
| `marca` | VARCHAR(50) | NÃO | — | — | Fabricante (ex: Toyota) |
| `modelo` | VARCHAR(100) | NÃO | — | — | Modelo (ex: Corolla) |
| `versao` | VARCHAR(100) | SIM | — | — | Versão/trim (ex: XEi AT) |
| `cor` | VARCHAR(50) | NÃO | — | — | Cor predominante |
| `ano_fabricacao` | SMALLINT | NÃO | — | — | Ano de fabricação |
| `ano_modelo` | SMALLINT | NÃO | — | — | Ano do modelo |
| `ar_condicionado` | BOOLEAN | NÃO | FALSE | — | Possui ar-condicionado |
| `mecanizacao` | tipo_mecanizacao_enum | NÃO | `MANUAL` | — | Manual ou automático |
| `tem_cadeirinha` | BOOLEAN | NÃO | FALSE | — | Suporte a cadeirinha infantil |
| `tem_bebe_conforto` | BOOLEAN | NÃO | FALSE | — | Suporte a bebê conforto |
| `num_portas` | SMALLINT | NÃO | — | IN (2,3,4,5) | Número de portas |
| `capacidade_pass` | SMALLINT | NÃO | — | 1–15 | Capacidade de passageiros |
| `combustivel` | VARCHAR(30) | NÃO | — | — | Tipo de combustível |
| `status` | status_veiculo_enum | NÃO | `DISPONIVEL` | — | Estado operacional |
| `km_atual` | NUMERIC(10,1) | NÃO | 0 | >= 0 | Quilometragem atual |
| `criado_em` | TIMESTAMP | NÃO | NOW() | — | Data de cadastro na frota |

---

### acessorio

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_acessorio` | SERIAL | NÃO | auto | PK | Identificador do acessório |
| `nome` | VARCHAR(100) | NÃO | — | UK | Nome do acessório (ex: GPS, teto solar) |
| `descricao` | VARCHAR(300) | SIM | — | — | Descrição detalhada |

---

### veiculo_acessorio

| Coluna | Tipo | Nulo | Restrições | Descrição |
|---|---|---|---|---|
| `id_veiculo` | INTEGER | NÃO | PK, FK veiculo | Veículo |
| `id_acessorio` | INTEGER | NÃO | PK, FK acessorio | Acessório |

---

### foto

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_foto` | SERIAL | NÃO | auto | PK | Identificador da foto |
| `id_veiculo` | INTEGER | NÃO | — | FK veiculo | Veículo fotografado |
| `id_locacao` | INTEGER | SIM | — | FK locacao | Preenchido para fotos de entrega/devolução |
| `url` | VARCHAR(500) | NÃO | — | — | URL de armazenamento |
| `tipo` | tipo_foto_enum | NÃO | — | — | Contexto da foto |
| `data_foto` | TIMESTAMP | NÃO | NOW() | — | Data/hora da foto |
| `descricao` | VARCHAR(300) | SIM | — | — | Observações (danos, odômetro, etc.) |

**Regra de negócio:** `tipo = 'PROPAGANDA'` implica `id_locacao IS NULL`; `tipo IN ('ENTREGA','DEVOLUCAO')` implica `id_locacao IS NOT NULL`.

---

### prontuario_veiculo

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_registro` | SERIAL | NÃO | auto | PK | Identificador do registro |
| `id_veiculo` | INTEGER | NÃO | — | FK veiculo | Veículo do prontuário |
| `data_registro` | TIMESTAMP | NÃO | NOW() | — | Data da ocorrência |
| `tipo_registro` | tipo_registro_enum | NÃO | — | — | Tipo do registro |
| `descricao` | TEXT | SIM | — | — | Detalhamento do serviço realizado |
| `km_atual` | NUMERIC(10,1) | NÃO | — | >= 0 | KM no momento do registro |
| `nivel_oleo` | nivel_fluido_enum | SIM | — | — | Nível de óleo observado |
| `pressao_pneu_dd` | NUMERIC(4,1) | SIM | — | — | Pressão pneu dianteiro direito (psi) |
| `pressao_pneu_de` | NUMERIC(4,1) | SIM | — | — | Pressão pneu dianteiro esquerdo (psi) |
| `pressao_pneu_td` | NUMERIC(4,1) | SIM | — | — | Pressão pneu traseiro direito (psi) |
| `pressao_pneu_te` | NUMERIC(4,1) | SIM | — | — | Pressão pneu traseiro esquerdo (psi) |
| `proxima_revisao_km` | NUMERIC(10,1) | SIM | — | — | KM para próxima revisão |
| `responsavel` | VARCHAR(150) | SIM | — | — | Nome do mecânico/responsável |

---

### cliente

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_cliente` | SERIAL | NÃO | auto | PK | Identificador do cliente |
| `tipo` | tipo_cliente_enum | NÃO | — | — | PF ou PJ |
| `email` | VARCHAR(150) | NÃO | — | UK | E-mail (login) |
| `telefone` | VARCHAR(20) | SIM | — | — | Telefone de contato |
| `logradouro` | VARCHAR(200) | SIM | — | — | Endereço |
| `numero` | VARCHAR(10) | SIM | — | — | Número |
| `complemento` | VARCHAR(100) | SIM | — | — | Complemento |
| `bairro` | VARCHAR(100) | SIM | — | — | Bairro |
| `cidade` | VARCHAR(100) | SIM | — | — | Cidade |
| `estado` | CHAR(2) | SIM | — | — | UF |
| `cep` | CHAR(8) | SIM | — | — | CEP sem hífen |
| `data_cadastro` | TIMESTAMP | NÃO | NOW() | — | Data de cadastro |
| `ativo` | BOOLEAN | NÃO | TRUE | — | Cliente ativo no sistema |

---

### cliente_pf

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_cliente` | INTEGER | NÃO | — | PK, FK cliente | Mesmo id de cliente |
| `cpf` | CHAR(11) | NÃO | — | UK | CPF sem formatação |
| `nome` | VARCHAR(100) | NÃO | — | — | Primeiro nome |
| `sobrenome` | VARCHAR(100) | NÃO | — | — | Sobrenome |
| `data_nascimento` | DATE | NÃO | — | — | Data de nascimento |
| `rg` | VARCHAR(20) | SIM | — | — | RG |

---

### cliente_pj

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_cliente` | INTEGER | NÃO | — | PK, FK cliente | Mesmo id de cliente |
| `cnpj` | CHAR(14) | NÃO | — | UK | CNPJ sem formatação |
| `razao_social` | VARCHAR(200) | NÃO | — | — | Razão social |
| `nome_fantasia` | VARCHAR(200) | SIM | — | — | Nome fantasia |
| `inscricao_estadual` | VARCHAR(30) | SIM | — | — | IE |

---

### condutor

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_condutor` | SERIAL | NÃO | auto | PK | Identificador do condutor |
| `id_cliente_pf` | INTEGER | SIM | — | FK cliente_pf | Se o condutor é cliente PF |
| `id_cliente_pj` | INTEGER | SIM | — | FK cliente_pj | Se o condutor é funcionário de PJ |
| `nome` | VARCHAR(200) | NÃO | — | — | Nome completo do condutor |
| `cpf` | CHAR(11) | NÃO | — | UK | CPF do condutor |
| `num_cnh` | VARCHAR(20) | NÃO | — | UK | Número da CNH |
| `categoria_cnh` | categoria_cnh_enum | NÃO | — | — | Categoria de habilitação |
| `data_expiracao_cnh` | DATE | NÃO | — | — | Validade da CNH |
| `data_nascimento` | DATE | NÃO | — | — | Data de nascimento |
| `ativo` | BOOLEAN | NÃO | TRUE | — | Condutor habilitado no sistema |

---

### reserva

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_reserva` | SERIAL | NÃO | auto | PK | Identificador da reserva |
| `id_cliente` | INTEGER | NÃO | — | FK cliente | Cliente que realizou a reserva |
| `id_grupo` | INTEGER | NÃO | — | FK grupo_veiculo | Grupo desejado |
| `id_veiculo` | INTEGER | SIM | — | FK veiculo | Veículo específico (opcional) |
| `id_patio_retirada` | INTEGER | NÃO | — | FK patio | Pátio de retirada |
| `id_patio_devolucao` | INTEGER | NÃO | — | FK patio | Pátio de devolução |
| `data_reserva` | TIMESTAMP | NÃO | NOW() | — | Momento da reserva |
| `data_prevista_retirada` | TIMESTAMP | NÃO | — | — | Quando o cliente pretende retirar |
| `data_prevista_devolucao` | TIMESTAMP | NÃO | — | devolucao > retirada | Quando pretende devolver |
| `status` | status_reserva_enum | NÃO | `CONFIRMADA` | — | Estado da reserva |
| `valor_estimado` | NUMERIC(10,2) | SIM | — | — | Valor estimado em R$ |
| `observacoes` | TEXT | SIM | — | — | Observações livres |

---

### fila_espera

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_fila` | SERIAL | NÃO | auto | PK | Identificador na fila |
| `id_cliente` | INTEGER | NÃO | — | FK cliente | Cliente aguardando |
| `id_grupo` | INTEGER | NÃO | — | FK grupo_veiculo | Grupo desejado |
| `id_patio_retirada` | INTEGER | NÃO | — | FK patio | Pátio de retirada desejado |
| `data_solicitacao` | TIMESTAMP | NÃO | NOW() | — | Quando entrou na fila |
| `data_desejada` | TIMESTAMP | NÃO | — | — | Data desejada para retirada |
| `duracao_dias` | SMALLINT | NÃO | — | > 0 | Duração desejada em dias |
| `ativo` | BOOLEAN | NÃO | TRUE | — | Posição ainda ativa na fila |
| `observacoes` | TEXT | SIM | — | — | Observações |

---

### locacao

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_locacao` | SERIAL | NÃO | auto | PK | Identificador da locação |
| `id_reserva` | INTEGER | SIM | — | FK reserva, UK | Reserva de origem (opcional) |
| `id_cliente` | INTEGER | NÃO | — | FK cliente | Locatário |
| `id_condutor` | INTEGER | NÃO | — | FK condutor | Motorista do veículo |
| `id_veiculo` | INTEGER | NÃO | — | FK veiculo | Veículo alugado |
| `id_patio_saida` | INTEGER | NÃO | — | FK patio | Pátio de retirada real |
| `id_patio_chegada` | INTEGER | SIM | — | FK patio | Pátio de devolução (preenchido na devolução) |
| `data_hora_prevista_retirada` | TIMESTAMP | NÃO | — | — | Retirada prevista em contrato |
| `data_hora_retirada` | TIMESTAMP | SIM | — | — | Retirada real |
| `data_hora_prevista_devolucao` | TIMESTAMP | NÃO | — | devolucao > retirada | Devolução prevista em contrato |
| `data_hora_devolucao` | TIMESTAMP | SIM | — | — | Devolução real |
| `km_saida` | NUMERIC(10,1) | NÃO | — | >= 0 | Quilometragem na entrega |
| `km_chegada` | NUMERIC(10,1) | SIM | — | >= km_saida | Quilometragem na devolução |
| `status` | status_locacao_enum | NÃO | `ATIVA` | — | Estado da locação |
| `observacoes_entrega` | TEXT | SIM | — | — | Estado do veículo na entrega |
| `observacoes_devolucao` | TEXT | SIM | — | — | Estado do veículo na devolução |
| `criado_em` | TIMESTAMP | NÃO | NOW() | — | Data de abertura do contrato |

---

### protecao_adicional

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_protecao` | SERIAL | NÃO | auto | PK | Identificador da proteção |
| `nome` | VARCHAR(100) | NÃO | — | UK | Nome (ex: "Proteção de Vidros") |
| `descricao` | TEXT | SIM | — | — | Cobertura detalhada |
| `valor_adicional_diaria` | NUMERIC(10,2) | NÃO | — | >= 0 | Valor adicional por diária em R$ |
| `ativo` | BOOLEAN | NÃO | TRUE | — | Proteção disponível para contratação |

---

### locacao_protecao

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_locacao` | INTEGER | NÃO | — | PK, FK locacao | Locação |
| `id_protecao` | INTEGER | NÃO | — | PK, FK protecao_adicional | Proteção contratada |
| `valor_cobrado_diaria` | NUMERIC(10,2) | NÃO | — | >= 0 | Valor cobrado (pode diferir do tabela se houver desconto) |

---

### cobranca

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_cobranca` | SERIAL | NÃO | auto | PK | Identificador da cobrança |
| `id_locacao` | INTEGER | NÃO | — | FK locacao | Locação cobrada |
| `tipo` | tipo_cobranca_enum | NÃO | `INICIAL` | UK(locacao,tipo) | INICIAL = estimativa; FINAL = ajuste real |
| `data_emissao` | TIMESTAMP | NÃO | NOW() | — | Data de emissão |
| `data_vencimento` | DATE | NÃO | — | — | Vencimento |
| `data_pagamento` | TIMESTAMP | SIM | — | — | Data do pagamento (NULL = não pago) |
| `num_diarias` | NUMERIC(8,2) | NÃO | — | > 0 | Número de diárias cobradas |
| `valor_diaria` | NUMERIC(10,2) | NÃO | — | > 0 | Valor da diária aplicado (R$) |
| `valor_protecoes` | NUMERIC(10,2) | NÃO | 0 | >= 0 | Total das proteções contratadas (R$) |
| `valor_km_excedente` | NUMERIC(10,2) | NÃO | 0 | >= 0 | Cobrança por KM acima do contrato (R$) |
| `valor_outros` | NUMERIC(10,2) | NÃO | 0 | — | Multas, combustível, etc. (R$) |
| `valor_total` | NUMERIC(10,2) | NÃO | — | >= 0 | Valor total (R$) |
| `status` | status_cobranca_enum | NÃO | `PENDENTE` | — | Estado do pagamento |
| `forma_pagamento` | forma_pagamento_enum | SIM | — | — | Forma de pagamento utilizada |
| `num_transacao` | VARCHAR(100) | SIM | — | — | ID da transação/NSU |
| `observacoes` | TEXT | SIM | — | — | Observações livres |

---

### veiculo_patio

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id_movimentacao` | SERIAL | NÃO | auto | PK | Identificador da movimentação |
| `id_veiculo` | INTEGER | NÃO | — | FK veiculo | Veículo movimentado |
| `id_vaga` | INTEGER | NÃO | — | FK vaga | Vaga ocupada |
| `id_locacao` | INTEGER | SIM | — | FK locacao | Locação que gerou a saída (NULL = movimento interno) |
| `data_entrada` | TIMESTAMP | NÃO | NOW() | — | Chegada na vaga |
| `data_saida` | TIMESTAMP | SIM | — | saida > entrada | Saída da vaga (NULL = veículo ainda lá) |

**Uso para Markov:** Para cada locação concluída, cruzar o `id_patio` da vaga de saída (via `veiculo_patio` com `id_locacao` e a `data_saida` mais antiga) com o `id_patio` da vaga de chegada (registro com `data_entrada` correspondente à devolução). O resultado alimenta a matriz de transição entre pátios.

---

## Restrições de Integridade — Resumo

| Tabela | Restrição | Tipo | Definição |
|---|---|---|---|
| `vaga` | `(id_patio, codigo)` | UK | Código único por pátio |
| `foto` | `chk_foto_tipo` | CHECK | PROPAGANDA ↔ sem locação; ENTREGA/DEVOLUCAO ↔ com locação |
| `reserva` | `chk_reserva_datas` | CHECK | devolução prevista > retirada prevista |
| `locacao` | `chk_locacao_datas` | CHECK | devolução prevista > retirada prevista |
| `locacao` | `chk_locacao_km` | CHECK | km_chegada ≥ km_saida |
| `locacao` | `id_reserva` | UK | Cada reserva gera no máximo uma locação |
| `cobranca` | `(id_locacao, tipo)` | UK | Máximo uma cobrança INICIAL e uma FINAL por locação |
| `veiculo_patio` | `chk_vp_datas` | CHECK | data_saida > data_entrada |
| `grupo_veiculo` | `valor_diaria_base` | CHECK | > 0 |
| `veiculo` | `num_portas` | CHECK | IN (2, 3, 4, 5) |
| `veiculo` | `capacidade_pass` | CHECK | BETWEEN 1 AND 15 |
| `veiculo` | `km_atual` | CHECK | >= 0 |
| `fila_espera` | `duracao_dias` | CHECK | > 0 |
