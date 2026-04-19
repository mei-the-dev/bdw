# Modelo Conceitual — Locadora de Veículos
## MAE016 — 2026.1 | Grupo: [NOMES E DRE]

---

## Descrição das Entidades e Relacionamentos

### Entidades Principais

| Entidade | Descrição |
|---|---|
| **EMPRESA** | A empresa locadora dona do sistema. Proprietária de veículos e pátios. |
| **PÁTIO** | Local físico de retirada/devolução. Pertence a uma empresa mas serve a todas. |
| **VAGA** | Posição individual no pátio, identificada por código alfanumérico. |
| **GRUPO_VEÍCULO** | Categoria da locadora (ex: econômico, SUV, luxo). Define faixa de preço. |
| **VEÍCULO** | Unidade da frota. Tem empresa proprietária mas circula por todos os pátios. |
| **ACESSÓRIO** | Característica opcional do veículo (GPS, teto solar, rack, etc.). |
| **FOTO** | Fotos de propaganda ou de inspeção na entrega/devolução. |
| **PRONTUÁRIO** | Histórico de revisões, inspeções e manutenções de cada veículo. |
| **CLIENTE** | Supertipo: pessoa física (PF) ou jurídica (PJ). |
| **CONDUTOR** | Motorista habilitado. Pode ser o cliente PF, funcionário de PJ ou terceiro. |
| **RESERVA** | Intenção de locação: grupo + pátio retirada + pátio devolução + janela de tempo. |
| **FILA DE ESPERA** | Demanda reprimida para grupos especiais ou de alta procura. |
| **LOCAÇÃO** | Contrato efetivo. Registra retirada real, devolução real, KM, condutor. |
| **PROTEÇÃO ADICIONAL** | Cobertura opcional contratável na locação (ex: proteção de vidros). |
| **COBRANÇA** | Fatura da locação; pode ser inicial (estimativa) e final (ajuste). |
| **VEÍCULO_PÁTIO** | Histórico de onde cada veículo esteve — base para a análise de Markov. |

---

## Diagrama Entidade-Relacionamento

```mermaid
erDiagram
    EMPRESA {
        int     id_empresa      PK
        char    cnpj            UK
        varchar razao_social
        varchar nome_fantasia
        bool    ativo
    }

    PATIO {
        int     id_patio        PK
        int     id_empresa      FK
        varchar nome
        varchar cidade
        char    estado
        int     capacidade_total
        bool    ativo
    }

    VAGA {
        int     id_vaga         PK
        int     id_patio        FK
        varchar codigo
        enum    status
    }

    GRUPO_VEICULO {
        int     id_grupo        PK
        varchar codigo          UK
        varchar descricao
        numeric valor_diaria_base
        bool    ativo
    }

    VEICULO {
        int     id_veiculo      PK
        int     id_grupo        FK
        int     id_empresa      FK
        varchar placa           UK
        varchar chassi          UK
        varchar marca
        varchar modelo
        varchar cor
        smallint ano_fabricacao
        enum    mecanizacao
        bool    ar_condicionado
        bool    tem_cadeirinha
        bool    tem_bebe_conforto
        enum    status
        numeric km_atual
    }

    ACESSORIO {
        int     id_acessorio    PK
        varchar nome            UK
    }

    VEICULO_ACESSORIO {
        int id_veiculo          FK
        int id_acessorio        FK
    }

    FOTO {
        int       id_foto       PK
        int       id_veiculo    FK
        int       id_locacao    FK
        varchar   url
        enum      tipo
        timestamp data_foto
    }

    PRONTUARIO_VEICULO {
        int       id_registro   PK
        int       id_veiculo    FK
        timestamp data_registro
        enum      tipo_registro
        numeric   km_atual
        enum      nivel_oleo
    }

    CLIENTE {
        int       id_cliente    PK
        enum      tipo
        varchar   email         UK
        varchar   cidade
        timestamp data_cadastro
        bool      ativo
    }

    CLIENTE_PF {
        int  id_cliente         PK_FK
        char cpf                UK
        varchar nome
        varchar sobrenome
        date data_nascimento
    }

    CLIENTE_PJ {
        int  id_cliente         PK_FK
        char cnpj               UK
        varchar razao_social
        varchar nome_fantasia
    }

    CONDUTOR {
        int  id_condutor        PK
        int  id_cliente_pf      FK
        int  id_cliente_pj      FK
        varchar nome
        char cpf                UK
        varchar num_cnh         UK
        enum categoria_cnh
        date data_expiracao_cnh
    }

    RESERVA {
        int       id_reserva            PK
        int       id_cliente            FK
        int       id_grupo              FK
        int       id_veiculo            FK
        int       id_patio_retirada     FK
        int       id_patio_devolucao    FK
        timestamp data_reserva
        timestamp data_prevista_retirada
        timestamp data_prevista_devolucao
        enum      status
        numeric   valor_estimado
    }

    FILA_ESPERA {
        int       id_fila           PK
        int       id_cliente        FK
        int       id_grupo          FK
        int       id_patio_retirada FK
        timestamp data_solicitacao
        smallint  duracao_dias
        bool      ativo
    }

    LOCACAO {
        int       id_locacao                    PK
        int       id_reserva                    FK
        int       id_cliente                    FK
        int       id_condutor                   FK
        int       id_veiculo                    FK
        int       id_patio_saida                FK
        int       id_patio_chegada              FK
        timestamp data_hora_retirada
        timestamp data_hora_devolucao
        numeric   km_saida
        numeric   km_chegada
        enum      status
    }

    PROTECAO_ADICIONAL {
        int     id_protecao     PK
        varchar nome            UK
        numeric valor_adicional_diaria
        bool    ativo
    }

    LOCACAO_PROTECAO {
        int     id_locacao      FK
        int     id_protecao     FK
        numeric valor_cobrado_diaria
    }

    COBRANCA {
        int       id_cobranca   PK
        int       id_locacao    FK
        enum      tipo
        timestamp data_emissao
        numeric   valor_total
        enum      status
        enum      forma_pagamento
    }

    VEICULO_PATIO {
        int       id_movimentacao   PK
        int       id_veiculo        FK
        int       id_vaga           FK
        int       id_locacao        FK
        timestamp data_entrada
        timestamp data_saida
    }

    EMPRESA        ||--|{ PATIO              : "possui"
    EMPRESA        ||--|{ VEICULO            : "proprietária"
    PATIO          ||--|{ VAGA               : "contém"
    GRUPO_VEICULO  ||--|{ VEICULO            : "classifica"
    VEICULO        ||--o{ VEICULO_ACESSORIO  : "possui"
    ACESSORIO      ||--o{ VEICULO_ACESSORIO  : "compõe"
    VEICULO        ||--o{ FOTO               : "registrada"
    VEICULO        ||--o{ PRONTUARIO_VEICULO : "possui"
    CLIENTE        ||--o| CLIENTE_PF         : "é"
    CLIENTE        ||--o| CLIENTE_PJ         : "é"
    CLIENTE_PF     ||--o{ CONDUTOR           : "pode ser"
    CLIENTE_PJ     ||--o{ CONDUTOR           : "autoriza"
    CLIENTE        ||--o{ RESERVA            : "realiza"
    GRUPO_VEICULO  ||--o{ RESERVA            : "solicitado em"
    VEICULO        ||--o{ RESERVA            : "específico em"
    PATIO          ||--o{ RESERVA            : "retirada"
    PATIO          ||--o{ RESERVA            : "devolução"
    CLIENTE        ||--o{ FILA_ESPERA        : "entra em"
    GRUPO_VEICULO  ||--o{ FILA_ESPERA        : "aguardado"
    PATIO          ||--o{ FILA_ESPERA        : "pátio desejado"
    RESERVA        ||--o| LOCACAO            : "origina"
    CLIENTE        ||--o{ LOCACAO            : "contrata"
    CONDUTOR       ||--o{ LOCACAO            : "conduz"
    VEICULO        ||--o{ LOCACAO            : "alugado"
    PATIO          ||--o{ LOCACAO            : "saída"
    PATIO          ||--o{ LOCACAO            : "chegada"
    LOCACAO        ||--o{ FOTO               : "documenta"
    LOCACAO        ||--o{ LOCACAO_PROTECAO   : "contrata"
    PROTECAO_ADICIONAL ||--o{ LOCACAO_PROTECAO : "em"
    LOCACAO        ||--o{ COBRANCA           : "gera"
    VEICULO        ||--o{ VEICULO_PATIO      : "posicionado"
    VAGA           ||--o{ VEICULO_PATIO      : "ocupa"
    LOCACAO        ||--o{ VEICULO_PATIO      : "registra"
```

---

## Decisões de Modelagem

1. **Herança de CLIENTE** — Tabela-por-subtipo (table-per-subtype): `cliente` guarda atributos comuns; `cliente_pf` e `cliente_pj` estendem com PK = FK. Mantém integridade e permite joins simples.

2. **CONDUTOR separado de CLIENTE** — O motorista pode ser: (a) o próprio cliente PF, (b) funcionário autorizado por um cliente PJ, ou (c) terceiro não cadastrado. As FKs opcionais `id_cliente_pf` e `id_cliente_pj` suportam todos os casos.

3. **FOTO com FK opcional para LOCAÇÃO** — Fotos de propaganda têm `id_locacao = NULL`; fotos de entrega/devolução têm `id_locacao` preenchido. A constraint `chk_foto_tipo` faz isso em nível de banco.

4. **VEÍCULO_PÁTIO como entidade de histórico** — Cada movimentação (entrada/saída de vaga) é um registro separado. `data_saida IS NULL` = veículo ainda lá. Esse histórico é a fonte direta para a matriz estocástica de Markov.

5. **COBRANÇA com tipo INICIAL/FINAL** — Permite cobrança antecipada e ajuste na devolução sem duplicar lógica ou reabrir registros.

6. **id_empresa em VEÍCULO** — Necessário para os relatórios gerenciais de "origem" do veículo no pátio (frota da empresa proprietária vs. frota de associadas).
