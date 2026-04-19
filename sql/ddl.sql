-- ============================================================
-- LOCADORA DE VEÍCULOS — Modelo Físico (SQL DDL)
-- MAE016 — Bancos de Dados e Big Data — UFRJ / NCE — 2026.1
-- Grupo: [NOMES COMPLETOS E DRE]
-- Data: 2026-04-18
-- Padrão: ANSI SQL:2003 / PostgreSQL 15+
-- ============================================================

-- ============================================================
-- SCHEMA
-- ============================================================
CREATE SCHEMA IF NOT EXISTS locadora;
SET search_path = locadora;

-- ============================================================
-- TIPOS ENUMERADOS
-- ============================================================
CREATE TYPE tipo_cliente_enum       AS ENUM ('PF', 'PJ');
CREATE TYPE status_veiculo_enum     AS ENUM ('DISPONIVEL', 'ALUGADO', 'MANUTENCAO', 'INATIVO');
CREATE TYPE tipo_mecanizacao_enum   AS ENUM ('MANUAL', 'AUTOMATICA');
CREATE TYPE status_vaga_enum        AS ENUM ('LIVRE', 'OCUPADA', 'RESERVADA', 'MANUTENCAO');
CREATE TYPE tipo_foto_enum          AS ENUM ('PROPAGANDA', 'ENTREGA', 'DEVOLUCAO');
CREATE TYPE tipo_registro_enum      AS ENUM ('REVISAO', 'INSPECAO', 'MANUTENCAO_CORRETIVA', 'MANUTENCAO_PREVENTIVA');
CREATE TYPE nivel_fluido_enum       AS ENUM ('OK', 'BAIXO', 'CRITICO');
CREATE TYPE categoria_cnh_enum      AS ENUM ('A', 'B', 'C', 'D', 'E', 'AB', 'AC', 'AD', 'AE');
CREATE TYPE status_reserva_enum     AS ENUM ('CONFIRMADA', 'CANCELADA', 'EM_ESPERA', 'CONCLUIDA', 'EXPIRADA');
CREATE TYPE status_locacao_enum     AS ENUM ('ATIVA', 'CONCLUIDA', 'CANCELADA');
CREATE TYPE tipo_cobranca_enum      AS ENUM ('INICIAL', 'FINAL', 'ADICIONAL');
CREATE TYPE status_cobranca_enum    AS ENUM ('PENDENTE', 'PAGO', 'CANCELADO', 'ATRASADO');
CREATE TYPE forma_pagamento_enum    AS ENUM ('CARTAO_CREDITO', 'CARTAO_DEBITO', 'PIX', 'BOLETO', 'DINHEIRO');

-- ============================================================
-- 1. EMPRESA
-- A empresa proprietária do sistema operativo (uma das seis).
-- Registrada também no DW para identificar origem dos veículos.
-- ============================================================
CREATE TABLE empresa (
    id_empresa      SERIAL          PRIMARY KEY,
    cnpj            CHAR(14)        NOT NULL UNIQUE,
    razao_social    VARCHAR(200)    NOT NULL,
    nome_fantasia   VARCHAR(200),
    email           VARCHAR(150),
    telefone        VARCHAR(20),
    ativo           BOOLEAN         NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. PÁTIO
-- Local físico de retirada e devolução de veículos.
-- Um pátio pertence a uma empresa mas aceita veículos de todas.
-- ============================================================
CREATE TABLE patio (
    id_patio            SERIAL          PRIMARY KEY,
    id_empresa          INTEGER         NOT NULL
                            REFERENCES empresa(id_empresa) ON DELETE RESTRICT,
    nome                VARCHAR(150)    NOT NULL,
    logradouro          VARCHAR(200)    NOT NULL,
    numero              VARCHAR(10),
    complemento         VARCHAR(100),
    bairro              VARCHAR(100),
    cidade              VARCHAR(100)    NOT NULL,
    estado              CHAR(2)         NOT NULL,
    cep                 CHAR(8)         NOT NULL,
    capacidade_total    INTEGER         NOT NULL CHECK (capacidade_total > 0),
    ativo               BOOLEAN         NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 3. VAGA
-- Vaga individual identificada por código alfanumérico.
-- O código é único dentro de cada pátio.
-- ============================================================
CREATE TABLE vaga (
    id_vaga     SERIAL              PRIMARY KEY,
    id_patio    INTEGER             NOT NULL
                    REFERENCES patio(id_patio) ON DELETE RESTRICT,
    codigo      VARCHAR(10)         NOT NULL,
    status      status_vaga_enum    NOT NULL DEFAULT 'LIVRE',
    UNIQUE (id_patio, codigo)
);

-- ============================================================
-- 4. GRUPO DE VEÍCULO
-- Categoria/grupo definida pela locadora; resume luxo e faixa
-- de preço. Ponto de partida da escolha do cliente.
-- ============================================================
CREATE TABLE grupo_veiculo (
    id_grupo            SERIAL          PRIMARY KEY,
    codigo              VARCHAR(10)     NOT NULL UNIQUE,
    descricao           VARCHAR(200)    NOT NULL,
    valor_diaria_base   NUMERIC(10,2)   NOT NULL CHECK (valor_diaria_base > 0),
    descricao_luxo      VARCHAR(500),
    ativo               BOOLEAN         NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 5. VEÍCULO
-- Frota de veículos da empresa. Cada veículo tem empresa
-- proprietária, mas pode circular por todos os seis pátios.
-- ============================================================
CREATE TABLE veiculo (
    id_veiculo          SERIAL                  PRIMARY KEY,
    id_grupo            INTEGER                 NOT NULL
                            REFERENCES grupo_veiculo(id_grupo),
    id_empresa          INTEGER                 NOT NULL
                            REFERENCES empresa(id_empresa),
    placa               VARCHAR(8)              NOT NULL UNIQUE,
    chassi              VARCHAR(17)             NOT NULL UNIQUE,
    marca               VARCHAR(50)             NOT NULL,
    modelo              VARCHAR(100)            NOT NULL,
    versao              VARCHAR(100),
    cor                 VARCHAR(50)             NOT NULL,
    ano_fabricacao      SMALLINT                NOT NULL,
    ano_modelo          SMALLINT                NOT NULL,
    ar_condicionado     BOOLEAN                 NOT NULL DEFAULT FALSE,
    mecanizacao         tipo_mecanizacao_enum   NOT NULL DEFAULT 'MANUAL',
    tem_cadeirinha      BOOLEAN                 NOT NULL DEFAULT FALSE,
    tem_bebe_conforto   BOOLEAN                 NOT NULL DEFAULT FALSE,
    num_portas          SMALLINT                NOT NULL CHECK (num_portas IN (2, 3, 4, 5)),
    capacidade_pass     SMALLINT                NOT NULL CHECK (capacidade_pass BETWEEN 1 AND 15),
    combustivel         VARCHAR(30)             NOT NULL,
    status              status_veiculo_enum     NOT NULL DEFAULT 'DISPONIVEL',
    km_atual            NUMERIC(10,1)           NOT NULL DEFAULT 0 CHECK (km_atual >= 0),
    criado_em           TIMESTAMP               NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. ACESSÓRIO
-- ============================================================
CREATE TABLE acessorio (
    id_acessorio    SERIAL          PRIMARY KEY,
    nome            VARCHAR(100)    NOT NULL UNIQUE,
    descricao       VARCHAR(300)
);

-- ============================================================
-- 7. VEÍCULO_ACESSÓRIO (N:N)
-- ============================================================
CREATE TABLE veiculo_acessorio (
    id_veiculo      INTEGER     NOT NULL
                        REFERENCES veiculo(id_veiculo)    ON DELETE CASCADE,
    id_acessorio    INTEGER     NOT NULL
                        REFERENCES acessorio(id_acessorio) ON DELETE CASCADE,
    PRIMARY KEY (id_veiculo, id_acessorio)
);

-- ============================================================
-- 8. FOTO
-- Fotos de propaganda (sem locação) e de inspeção na entrega
-- e devolução (com locação). FK para locacao adicionada depois.
-- ============================================================
CREATE TABLE foto (
    id_foto         SERIAL          PRIMARY KEY,
    id_veiculo      INTEGER         NOT NULL
                        REFERENCES veiculo(id_veiculo),
    id_locacao      INTEGER,
    url             VARCHAR(500)    NOT NULL,
    tipo            tipo_foto_enum  NOT NULL,
    data_foto       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descricao       VARCHAR(300),
    CONSTRAINT chk_foto_tipo CHECK (
        (tipo = 'PROPAGANDA' AND id_locacao IS NULL) OR
        (tipo IN ('ENTREGA', 'DEVOLUCAO') AND id_locacao IS NOT NULL)
    )
);

-- ============================================================
-- 9. PRONTUÁRIO DO VEÍCULO
-- Histórico de revisões, inspeções e manutenções.
-- ============================================================
CREATE TABLE prontuario_veiculo (
    id_registro         SERIAL                  PRIMARY KEY,
    id_veiculo          INTEGER                 NOT NULL
                            REFERENCES veiculo(id_veiculo),
    data_registro       TIMESTAMP               NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_registro       tipo_registro_enum      NOT NULL,
    descricao           TEXT,
    km_atual            NUMERIC(10,1)           NOT NULL CHECK (km_atual >= 0),
    nivel_oleo          nivel_fluido_enum,
    pressao_pneu_dd     NUMERIC(4,1),
    pressao_pneu_de     NUMERIC(4,1),
    pressao_pneu_td     NUMERIC(4,1),
    pressao_pneu_te     NUMERIC(4,1),
    proxima_revisao_km  NUMERIC(10,1),
    responsavel         VARCHAR(150)
);

-- ============================================================
-- 10. CLIENTE (SUPERTIPO)
-- PF ou PJ; subtipo determinado por tipo e tabela associada.
-- ============================================================
CREATE TABLE cliente (
    id_cliente      SERIAL              PRIMARY KEY,
    tipo            tipo_cliente_enum   NOT NULL,
    email           VARCHAR(150)        NOT NULL UNIQUE,
    telefone        VARCHAR(20),
    logradouro      VARCHAR(200),
    numero          VARCHAR(10),
    complemento     VARCHAR(100),
    bairro          VARCHAR(100),
    cidade          VARCHAR(100),
    estado          CHAR(2),
    cep             CHAR(8),
    data_cadastro   TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo           BOOLEAN             NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 11. CLIENTE PESSOA FÍSICA
-- ============================================================
CREATE TABLE cliente_pf (
    id_cliente      INTEGER         PRIMARY KEY
                        REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    cpf             CHAR(11)        NOT NULL UNIQUE,
    nome            VARCHAR(100)    NOT NULL,
    sobrenome       VARCHAR(100)    NOT NULL,
    data_nascimento DATE            NOT NULL,
    rg              VARCHAR(20)
);

-- ============================================================
-- 12. CLIENTE PESSOA JURÍDICA
-- ============================================================
CREATE TABLE cliente_pj (
    id_cliente          INTEGER         PRIMARY KEY
                            REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    cnpj                CHAR(14)        NOT NULL UNIQUE,
    razao_social        VARCHAR(200)    NOT NULL,
    nome_fantasia       VARCHAR(200),
    inscricao_estadual  VARCHAR(30)
);

-- ============================================================
-- 13. CONDUTOR
-- Motorista habilitado. Pode ser:
--   (a) O próprio cliente PF → id_cliente_pf preenchido
--   (b) Funcionário de PJ   → id_cliente_pj preenchido
--   (c) Terceiro autorizado → ambas FK nulas
-- ============================================================
CREATE TABLE condutor (
    id_condutor         SERIAL                  PRIMARY KEY,
    id_cliente_pf       INTEGER
                            REFERENCES cliente_pf(id_cliente),
    id_cliente_pj       INTEGER
                            REFERENCES cliente_pj(id_cliente),
    nome                VARCHAR(200)            NOT NULL,
    cpf                 CHAR(11)                NOT NULL UNIQUE,
    num_cnh             VARCHAR(20)             NOT NULL UNIQUE,
    categoria_cnh       categoria_cnh_enum      NOT NULL,
    data_expiracao_cnh  DATE                    NOT NULL,
    data_nascimento     DATE                    NOT NULL,
    ativo               BOOLEAN                 NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 14. RESERVA
-- Reserva por grupo (obrigatório) ou veículo específico
-- (opcional). Pátio de retirada e devolução independentes.
-- ============================================================
CREATE TABLE reserva (
    id_reserva                  SERIAL                  PRIMARY KEY,
    id_cliente                  INTEGER                 NOT NULL
                                    REFERENCES cliente(id_cliente),
    id_grupo                    INTEGER                 NOT NULL
                                    REFERENCES grupo_veiculo(id_grupo),
    id_veiculo                  INTEGER
                                    REFERENCES veiculo(id_veiculo),
    id_patio_retirada           INTEGER                 NOT NULL
                                    REFERENCES patio(id_patio),
    id_patio_devolucao          INTEGER                 NOT NULL
                                    REFERENCES patio(id_patio),
    data_reserva                TIMESTAMP               NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_prevista_retirada      TIMESTAMP               NOT NULL,
    data_prevista_devolucao     TIMESTAMP               NOT NULL,
    status                      status_reserva_enum     NOT NULL DEFAULT 'CONFIRMADA',
    valor_estimado              NUMERIC(10,2),
    observacoes                 TEXT,
    CONSTRAINT chk_reserva_datas CHECK (
        data_prevista_devolucao > data_prevista_retirada
    )
);

-- ============================================================
-- 15. FILA DE ESPERA
-- Para grupos especiais ou de alta demanda com desistências.
-- ============================================================
CREATE TABLE fila_espera (
    id_fila             SERIAL          PRIMARY KEY,
    id_cliente          INTEGER         NOT NULL
                            REFERENCES cliente(id_cliente),
    id_grupo            INTEGER         NOT NULL
                            REFERENCES grupo_veiculo(id_grupo),
    id_patio_retirada   INTEGER         NOT NULL
                            REFERENCES patio(id_patio),
    data_solicitacao    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_desejada       TIMESTAMP       NOT NULL,
    duracao_dias        SMALLINT        NOT NULL CHECK (duracao_dias > 0),
    ativo               BOOLEAN         NOT NULL DEFAULT TRUE,
    observacoes         TEXT
);

-- ============================================================
-- 16. LOCAÇÃO
-- Contrato efetivo de aluguel. Originado ou não de reserva.
-- Pátio de chegada pode ser diferente do pátio de saída.
-- ============================================================
CREATE TABLE locacao (
    id_locacao                      SERIAL                  PRIMARY KEY,
    id_reserva                      INTEGER                 UNIQUE
                                        REFERENCES reserva(id_reserva),
    id_cliente                      INTEGER                 NOT NULL
                                        REFERENCES cliente(id_cliente),
    id_condutor                     INTEGER                 NOT NULL
                                        REFERENCES condutor(id_condutor),
    id_veiculo                      INTEGER                 NOT NULL
                                        REFERENCES veiculo(id_veiculo),
    id_patio_saida                  INTEGER                 NOT NULL
                                        REFERENCES patio(id_patio),
    id_patio_chegada                INTEGER
                                        REFERENCES patio(id_patio),
    data_hora_prevista_retirada     TIMESTAMP               NOT NULL,
    data_hora_retirada              TIMESTAMP,
    data_hora_prevista_devolucao    TIMESTAMP               NOT NULL,
    data_hora_devolucao             TIMESTAMP,
    km_saida                        NUMERIC(10,1)           NOT NULL CHECK (km_saida >= 0),
    km_chegada                      NUMERIC(10,1),
    status                          status_locacao_enum     NOT NULL DEFAULT 'ATIVA',
    observacoes_entrega             TEXT,
    observacoes_devolucao           TEXT,
    criado_em                       TIMESTAMP               NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_locacao_datas CHECK (
        data_hora_prevista_devolucao > data_hora_prevista_retirada
    ),
    CONSTRAINT chk_locacao_km CHECK (
        km_chegada IS NULL OR km_chegada >= km_saida
    )
);

-- FK de foto para locacao (criada após tabela locacao existir)
ALTER TABLE foto
    ADD CONSTRAINT fk_foto_locacao
    FOREIGN KEY (id_locacao) REFERENCES locacao(id_locacao);

-- ============================================================
-- 17. PROTEÇÃO ADICIONAL
-- Coberturas opcionais além do seguro básico obrigatório.
-- ============================================================
CREATE TABLE protecao_adicional (
    id_protecao             SERIAL          PRIMARY KEY,
    nome                    VARCHAR(100)    NOT NULL UNIQUE,
    descricao               TEXT,
    valor_adicional_diaria  NUMERIC(10,2)   NOT NULL CHECK (valor_adicional_diaria >= 0),
    ativo                   BOOLEAN         NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 18. LOCAÇÃO_PROTEÇÃO (N:N)
-- ============================================================
CREATE TABLE locacao_protecao (
    id_locacao              INTEGER         NOT NULL
                                REFERENCES locacao(id_locacao) ON DELETE CASCADE,
    id_protecao             INTEGER         NOT NULL
                                REFERENCES protecao_adicional(id_protecao),
    valor_cobrado_diaria    NUMERIC(10,2)   NOT NULL CHECK (valor_cobrado_diaria >= 0),
    PRIMARY KEY (id_locacao, id_protecao)
);

-- ============================================================
-- 19. COBRANÇA
-- Pode haver cobrança INICIAL (estimada no ato da retirada)
-- e cobrança FINAL (ajustada na devolução com KM real, multas
-- e diárias extras). UNIQUE (id_locacao, tipo) garante no máx.
-- uma cobrança de cada tipo por locação.
-- ============================================================
CREATE TABLE cobranca (
    id_cobranca         SERIAL                  PRIMARY KEY,
    id_locacao          INTEGER                 NOT NULL
                            REFERENCES locacao(id_locacao),
    tipo                tipo_cobranca_enum      NOT NULL DEFAULT 'INICIAL',
    data_emissao        TIMESTAMP               NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_vencimento     DATE                    NOT NULL,
    data_pagamento      TIMESTAMP,
    num_diarias         NUMERIC(8,2)            NOT NULL CHECK (num_diarias > 0),
    valor_diaria        NUMERIC(10,2)           NOT NULL CHECK (valor_diaria > 0),
    valor_protecoes     NUMERIC(10,2)           NOT NULL DEFAULT 0 CHECK (valor_protecoes >= 0),
    valor_km_excedente  NUMERIC(10,2)           NOT NULL DEFAULT 0 CHECK (valor_km_excedente >= 0),
    valor_outros        NUMERIC(10,2)           NOT NULL DEFAULT 0,
    valor_total         NUMERIC(10,2)           NOT NULL CHECK (valor_total >= 0),
    status              status_cobranca_enum    NOT NULL DEFAULT 'PENDENTE',
    forma_pagamento     forma_pagamento_enum,
    num_transacao       VARCHAR(100),
    observacoes         TEXT,
    UNIQUE (id_locacao, tipo)
);

-- ============================================================
-- 20. VEÍCULO_PÁTIO
-- Histórico completo de onde cada veículo esteve.
-- data_saida NULL indica veículo ainda no pátio.
-- Essencial para calcular a matriz estocástica de Markov:
--   percentual de veículos entregues em cada pátio por origem.
-- ============================================================
CREATE TABLE veiculo_patio (
    id_movimentacao SERIAL          PRIMARY KEY,
    id_veiculo      INTEGER         NOT NULL
                        REFERENCES veiculo(id_veiculo),
    id_vaga         INTEGER         NOT NULL
                        REFERENCES vaga(id_vaga),
    id_locacao      INTEGER
                        REFERENCES locacao(id_locacao),
    data_entrada    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_saida      TIMESTAMP,
    CONSTRAINT chk_vp_datas CHECK (
        data_saida IS NULL OR data_saida > data_entrada
    )
);

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX idx_veiculo_grupo          ON veiculo(id_grupo);
CREATE INDEX idx_veiculo_status         ON veiculo(status);
CREATE INDEX idx_veiculo_empresa        ON veiculo(id_empresa);
CREATE INDEX idx_vaga_patio             ON vaga(id_patio);
CREATE INDEX idx_vaga_status            ON vaga(status);
CREATE INDEX idx_reserva_cliente        ON reserva(id_cliente);
CREATE INDEX idx_reserva_grupo          ON reserva(id_grupo);
CREATE INDEX idx_reserva_datas          ON reserva(data_prevista_retirada, data_prevista_devolucao);
CREATE INDEX idx_reserva_patio_ret      ON reserva(id_patio_retirada);
CREATE INDEX idx_reserva_patio_dev      ON reserva(id_patio_devolucao);
CREATE INDEX idx_reserva_status         ON reserva(status);
CREATE INDEX idx_locacao_cliente        ON locacao(id_cliente);
CREATE INDEX idx_locacao_veiculo        ON locacao(id_veiculo);
CREATE INDEX idx_locacao_status         ON locacao(status);
CREATE INDEX idx_locacao_patio_saida    ON locacao(id_patio_saida);
CREATE INDEX idx_locacao_patio_chegada  ON locacao(id_patio_chegada);
CREATE INDEX idx_locacao_datas          ON locacao(data_hora_prevista_retirada, data_hora_prevista_devolucao);
CREATE INDEX idx_prontuario_veiculo     ON prontuario_veiculo(id_veiculo);
CREATE INDEX idx_cobranca_locacao       ON cobranca(id_locacao);
CREATE INDEX idx_cobranca_status        ON cobranca(status);
CREATE INDEX idx_vp_veiculo_saida       ON veiculo_patio(id_veiculo, data_saida);
CREATE INDEX idx_vp_vaga_saida          ON veiculo_patio(id_vaga, data_saida);
CREATE INDEX idx_fila_grupo             ON fila_espera(id_grupo, ativo);

-- ============================================================
-- COMENTÁRIOS
-- ============================================================
COMMENT ON TABLE empresa            IS 'Empresa locadora proprietária do sistema operativo';
COMMENT ON TABLE patio              IS 'Pátio de estacionamento — ponto de retirada e devolução';
COMMENT ON TABLE vaga               IS 'Vaga individual, código único por pátio';
COMMENT ON TABLE grupo_veiculo      IS 'Grupo/categoria da locadora: define luxo e faixa de preço';
COMMENT ON TABLE veiculo            IS 'Frota; id_empresa indica proprietária, mas veículo circula em todos os pátios';
COMMENT ON TABLE acessorio          IS 'Acessório ou característica opcional do veículo';
COMMENT ON TABLE veiculo_acessorio  IS 'Associação N:N veículo ↔ acessório';
COMMENT ON TABLE foto               IS 'Fotos de propaganda (sem locação) e inspeção de entrega/devolução';
COMMENT ON TABLE prontuario_veiculo IS 'Histórico de revisões, inspeções e manutenções do veículo';
COMMENT ON TABLE cliente            IS 'Supertipo de cliente — subtipo determinado pelo campo tipo';
COMMENT ON TABLE cliente_pf         IS 'Dados específicos de pessoa física';
COMMENT ON TABLE cliente_pj         IS 'Dados específicos de pessoa jurídica';
COMMENT ON TABLE condutor           IS 'Motorista habilitado; pode ser o próprio cliente PF, funcionário de PJ ou terceiro';
COMMENT ON TABLE reserva            IS 'Reserva de veículo por grupo; pátio de retirada e devolução podem diferir';
COMMENT ON TABLE fila_espera        IS 'Fila de espera para grupos com alta demanda ou tipos especiais';
COMMENT ON TABLE locacao            IS 'Contrato efetivo de locação — coração do sistema operativo';
COMMENT ON TABLE protecao_adicional IS 'Coberturas opcionais além do seguro básico';
COMMENT ON TABLE locacao_protecao   IS 'Proteções adicionais contratadas por locação';
COMMENT ON TABLE cobranca           IS 'Cobrança por locação: INICIAL (estimada) e FINAL (ajustada)';
COMMENT ON TABLE veiculo_patio      IS 'Histórico de movimentações de veículos entre vagas — base para análise de Markov';
