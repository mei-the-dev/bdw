# Modelo Lógico — Locadora de Veículos
## MAE016 — 2026.1 | Grupo: [NOMES E DRE]

---

## Nível de Normalização

O modelo está na **Terceira Forma Normal (3FN)**:

- **1FN**: todos os atributos são atômicos; não há grupos repetidos.
- **2FN**: em todas as tabelas com chave primária composta (`veiculo_acessorio`, `locacao_protecao`), cada atributo não-chave depende da chave completa.
- **3FN**: não há dependências transitivas — cada atributo não-chave depende diretamente da PK da tabela.

---

## Representação Relacional

### Notação
`NomeTabela(`**PK**`, atributo, *FK*)`

---

### locadora.empresa
```
empresa(id_empresa, cnpj, razao_social, nome_fantasia, email, telefone, ativo, criado_em)
  PK: id_empresa
  UK: cnpj
```

### locadora.patio
```
patio(id_patio, *id_empresa*, nome, logradouro, numero, complemento, bairro, cidade, estado, cep, capacidade_total, ativo)
  PK: id_patio
  FK: id_empresa → empresa(id_empresa)
```

### locadora.vaga
```
vaga(id_vaga, *id_patio*, codigo, status)
  PK: id_vaga
  FK: id_patio → patio(id_patio)
  UK: (id_patio, codigo)
  CHECK: status IN ('LIVRE','OCUPADA','RESERVADA','MANUTENCAO')
```

### locadora.grupo_veiculo
```
grupo_veiculo(id_grupo, codigo, descricao, valor_diaria_base, descricao_luxo, ativo)
  PK: id_grupo
  UK: codigo
  CHECK: valor_diaria_base > 0
```

### locadora.veiculo
```
veiculo(id_veiculo, *id_grupo*, *id_empresa*, placa, chassi, marca, modelo, versao, cor,
        ano_fabricacao, ano_modelo, ar_condicionado, mecanizacao, tem_cadeirinha,
        tem_bebe_conforto, num_portas, capacidade_pass, combustivel, status, km_atual, criado_em)
  PK: id_veiculo
  FK: id_grupo → grupo_veiculo(id_grupo)
  FK: id_empresa → empresa(id_empresa)
  UK: placa
  UK: chassi
  CHECK: num_portas IN (2,3,4,5)
  CHECK: capacidade_pass BETWEEN 1 AND 15
  CHECK: km_atual >= 0
```

### locadora.acessorio
```
acessorio(id_acessorio, nome, descricao)
  PK: id_acessorio
  UK: nome
```

### locadora.veiculo_acessorio
```
veiculo_acessorio(*id_veiculo*, *id_acessorio*)
  PK: (id_veiculo, id_acessorio)
  FK: id_veiculo    → veiculo(id_veiculo)
  FK: id_acessorio  → acessorio(id_acessorio)
```

### locadora.foto
```
foto(id_foto, *id_veiculo*, *id_locacao*, url, tipo, data_foto, descricao)
  PK: id_foto
  FK: id_veiculo → veiculo(id_veiculo)
  FK: id_locacao → locacao(id_locacao)   [nullable]
  CHECK: tipo='PROPAGANDA' → id_locacao IS NULL
  CHECK: tipo IN ('ENTREGA','DEVOLUCAO') → id_locacao IS NOT NULL
```

### locadora.prontuario_veiculo
```
prontuario_veiculo(id_registro, *id_veiculo*, data_registro, tipo_registro, descricao,
                   km_atual, nivel_oleo, pressao_pneu_dd, pressao_pneu_de,
                   pressao_pneu_td, pressao_pneu_te, proxima_revisao_km, responsavel)
  PK: id_registro
  FK: id_veiculo → veiculo(id_veiculo)
  CHECK: km_atual >= 0
```

### locadora.cliente
```
cliente(id_cliente, tipo, email, telefone, logradouro, numero, complemento,
        bairro, cidade, estado, cep, data_cadastro, ativo)
  PK: id_cliente
  UK: email
  CHECK: tipo IN ('PF','PJ')
```

### locadora.cliente_pf
```
cliente_pf(*id_cliente*, cpf, nome, sobrenome, data_nascimento, rg)
  PK: id_cliente
  FK: id_cliente → cliente(id_cliente)
  UK: cpf
```

### locadora.cliente_pj
```
cliente_pj(*id_cliente*, cnpj, razao_social, nome_fantasia, inscricao_estadual)
  PK: id_cliente
  FK: id_cliente → cliente(id_cliente)
  UK: cnpj
```

### locadora.condutor
```
condutor(id_condutor, *id_cliente_pf*, *id_cliente_pj*, nome, cpf, num_cnh,
         categoria_cnh, data_expiracao_cnh, data_nascimento, ativo)
  PK: id_condutor
  FK: id_cliente_pf → cliente_pf(id_cliente)  [nullable]
  FK: id_cliente_pj → cliente_pj(id_cliente)  [nullable]
  UK: cpf
  UK: num_cnh
```

### locadora.reserva
```
reserva(id_reserva, *id_cliente*, *id_grupo*, *id_veiculo*, *id_patio_retirada*,
        *id_patio_devolucao*, data_reserva, data_prevista_retirada,
        data_prevista_devolucao, status, valor_estimado, observacoes)
  PK: id_reserva
  FK: id_cliente          → cliente(id_cliente)
  FK: id_grupo            → grupo_veiculo(id_grupo)
  FK: id_veiculo          → veiculo(id_veiculo)        [nullable]
  FK: id_patio_retirada   → patio(id_patio)
  FK: id_patio_devolucao  → patio(id_patio)
  CHECK: data_prevista_devolucao > data_prevista_retirada
```

### locadora.fila_espera
```
fila_espera(id_fila, *id_cliente*, *id_grupo*, *id_patio_retirada*,
            data_solicitacao, data_desejada, duracao_dias, ativo, observacoes)
  PK: id_fila
  FK: id_cliente          → cliente(id_cliente)
  FK: id_grupo            → grupo_veiculo(id_grupo)
  FK: id_patio_retirada   → patio(id_patio)
  CHECK: duracao_dias > 0
```

### locadora.locacao
```
locacao(id_locacao, *id_reserva*, *id_cliente*, *id_condutor*, *id_veiculo*,
        *id_patio_saida*, *id_patio_chegada*, data_hora_prevista_retirada,
        data_hora_retirada, data_hora_prevista_devolucao, data_hora_devolucao,
        km_saida, km_chegada, status, observacoes_entrega, observacoes_devolucao, criado_em)
  PK: id_locacao
  FK: id_reserva      → reserva(id_reserva)        [nullable, unique]
  FK: id_cliente      → cliente(id_cliente)
  FK: id_condutor     → condutor(id_condutor)
  FK: id_veiculo      → veiculo(id_veiculo)
  FK: id_patio_saida  → patio(id_patio)
  FK: id_patio_chegada → patio(id_patio)            [nullable]
  CHECK: data_hora_prevista_devolucao > data_hora_prevista_retirada
  CHECK: km_chegada IS NULL OR km_chegada >= km_saida
```

### locadora.protecao_adicional
```
protecao_adicional(id_protecao, nome, descricao, valor_adicional_diaria, ativo)
  PK: id_protecao
  UK: nome
  CHECK: valor_adicional_diaria >= 0
```

### locadora.locacao_protecao
```
locacao_protecao(*id_locacao*, *id_protecao*, valor_cobrado_diaria)
  PK: (id_locacao, id_protecao)
  FK: id_locacao  → locacao(id_locacao)
  FK: id_protecao → protecao_adicional(id_protecao)
  CHECK: valor_cobrado_diaria >= 0
```

### locadora.cobranca
```
cobranca(id_cobranca, *id_locacao*, tipo, data_emissao, data_vencimento, data_pagamento,
         num_diarias, valor_diaria, valor_protecoes, valor_km_excedente, valor_outros,
         valor_total, status, forma_pagamento, num_transacao, observacoes)
  PK: id_cobranca
  FK: id_locacao → locacao(id_locacao)
  UK: (id_locacao, tipo)
  CHECK: num_diarias > 0
  CHECK: valor_diaria > 0
  CHECK: valor_total >= 0
```

### locadora.veiculo_patio
```
veiculo_patio(id_movimentacao, *id_veiculo*, *id_vaga*, *id_locacao*, data_entrada, data_saida)
  PK: id_movimentacao
  FK: id_veiculo  → veiculo(id_veiculo)
  FK: id_vaga     → vaga(id_vaga)
  FK: id_locacao  → locacao(id_locacao)  [nullable]
  CHECK: data_saida IS NULL OR data_saida > data_entrada
```

---

## Cardinalidades Resumidas

| Relacionamento | Cardinalidade |
|---|---|
| empresa → patio | 1 : N |
| empresa → veiculo | 1 : N |
| patio → vaga | 1 : N |
| grupo_veiculo → veiculo | 1 : N |
| veiculo ↔ acessorio | N : N (via veiculo_acessorio) |
| veiculo → prontuario_veiculo | 1 : N |
| veiculo → foto | 1 : N |
| cliente → cliente_pf / cliente_pj | 1 : 0..1 (herança) |
| cliente → reserva | 1 : N |
| cliente → locacao | 1 : N |
| grupo_veiculo → reserva | 1 : N |
| reserva → locacao | 1 : 0..1 |
| locacao ↔ protecao_adicional | N : N (via locacao_protecao) |
| locacao → cobranca | 1 : 1..2 (INICIAL e/ou FINAL) |
| veiculo → veiculo_patio | 1 : N |
| vaga → veiculo_patio | 1 : N |
