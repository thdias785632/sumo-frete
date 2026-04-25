# Projeto: Minimizacao de Emissoes em Rota de Frete
## ESTU024-17 - Analise de Sistemas e Modelagem Ambiental (ASMA)
### UFABC - Engenharia Ambiental e Urbana

---

## Objetivo

Modelar e comparar as emissoes de poluentes (CO2, NOx, CO, HC, PMx)
de uma frota de caminhoes em tres rotas alternativas entre um Centro de
Distribuicao (A) e um cliente (B), identificando a rota que **minimiza
o impacto ambiental**.

O projeto utiliza o simulador **SUMO** (Simulation of Urban MObility)
com o modelo de emissao **HBEFA 3** para microssimulacao de trafego.

---

## Estrutura do Projeto

```
sumo-frete/
|
├── rede/
|   ├── input/
|   |   ├── nos.nod.xml               <- Nos (intersecoes) da rede
|   |   ├── vias.edg.xml              <- Vias (edges) com velocidade e faixas
|   |   └── semaforos.tll.xml          <- Definicao de semaforos
|   ├── gerar_rede.sh                 <- Script para gerar a rede (Linux/Mac)
|   ├── gerar_rede.bat                <- Script para gerar a rede (Windows)
|   └── rede_frete.net.xml            <- Rede gerada (saida do netconvert)
|
├── rotas/
|   ├── rotas_cenario_A.rou.xml       <- Rota Urbana, Euro IV
|   ├── rotas_cenario_B.rou.xml       <- Rota Arterial, Euro IV
|   ├── rotas_cenario_C.rou.xml       <- Rota Rodovia, Euro IV
|   └── rotas_cenario_D.rou.xml       <- Rota Urbana, Euro III
|
├── configs/
|   ├── simulacao_cenario_A.sumocfg   <- Rota Urbana (Euro IV)
|   ├── simulacao_cenario_B.sumocfg   <- Rota Arterial (Euro IV)
|   ├── simulacao_cenario_C.sumocfg   <- Rota Rodovia (Euro IV)
|   └── simulacao_cenario_D.sumocfg   <- Rota Urbana (Euro III)
|
├── resultados/                        <- (gerado pelo SUMO ao rodar)
|   ├── emissoes_cenario_*.xml
|   ├── tripinfo_cenario_*.xml
|   └── summary_cenario_*.xml
|
├── analise/
|   ├── analisar_emissoes.py           <- Script Python de analise e graficos
|   ├── tabela_emissoes.csv            <- Tabela comparativa (gerada)
|   ├── grafico_comparativo.png        <- CO2 e NOx por cenario (gerado)
|   └── grafico_detalhado.png          <- Todos os poluentes (gerado)
|
└── README.md                          <- Este arquivo
```

---

## Topologia da Rede

```
[A] --(via_1A)--> [N1] --(via_1B)--> [B]   <- ROTA 1: Urbana (5 km, 50 km/h)
 |                                    ^
 +--(via_2A)--> [N2] --(via_2B)------+     <- ROTA 2: Arterial (7 km, 70 km/h)
 |                                    |
 +--(via_3A)--> [N3] --(via_3B)------+     <- ROTA 3: Rodovia (9 km, 100 km/h)

A  = Origem  (Centro de Distribuicao)
B  = Destino (Cliente)
N1 = Semaforo com ciclo 60s verde / 40s vermelho
```

As tres rotas sao **geometricamente distintas**: a rota urbana segue em
linha reta, a arterial faz um desvio moderado ao sul, e a rodovia faz
um desvio maior, resultando em distancias e velocidades diferentes.

---

## Cenarios de Simulacao

| Cenario | Rota       | Veiculo  | Distancia | Vel. Max | Faixas | Semaforo |
|---------|------------|----------|-----------|----------|--------|----------|
| A       | Urbana     | Euro IV  | 5,0 km    | 50 km/h  | 1      | Sim      |
| B       | Arterial   | Euro IV  | 7,0 km    | 70 km/h  | 2      | Nao      |
| C       | Rodovia    | Euro IV  | 9,0 km    | 100 km/h | 2      | Nao      |
| D       | Urbana     | Euro III | 5,0 km    | 50 km/h  | 1      | Sim      |

> Cada cenario despacha **5 caminhoes** com intervalo de 60 segundos.

---

## Passo a Passo de Execucao

### 1. Instalar o SUMO

```bash
# Windows / Mac / Linux - baixar em:
# https://sumo.dlr.de/docs/Downloads.php

# Linux (Ubuntu/Debian):
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools

# Verificar instalacao:
sumo --version
```

### 2. Gerar a rede viaria (obrigatorio)

```bash
# Linux / Mac:
chmod +x rede/gerar_rede.sh
./rede/gerar_rede.sh

# Windows (CMD):
rede\gerar_rede.bat
```

Isso gera o `rede/rede_frete.net.xml` a partir dos nos e vias de entrada.

### 3. Rodar os cenarios

```bash
# Com interface grafica (recomendado para visualizacao):
sumo-gui -c configs/simulacao_cenario_A.sumocfg
sumo-gui -c configs/simulacao_cenario_B.sumocfg
sumo-gui -c configs/simulacao_cenario_C.sumocfg
sumo-gui -c configs/simulacao_cenario_D.sumocfg

# Sem interface (mais rapido, para analise):
sumo -c configs/simulacao_cenario_A.sumocfg
sumo -c configs/simulacao_cenario_B.sumocfg
sumo -c configs/simulacao_cenario_C.sumocfg
sumo -c configs/simulacao_cenario_D.sumocfg
```

### 4. Analisar os resultados

```bash
# Instalar dependencias Python:
pip install pandas matplotlib lxml

# Rodar analise:
python analise/analisar_emissoes.py
```

O script gera:
- **Tabela comparativa** com todos os poluentes (impressa no terminal)
- **tabela_emissoes.csv** - para importar no Excel
- **grafico_comparativo.png** - CO2 e NOx por cenario
- **grafico_detalhado.png** - todos os poluentes por cenario

---

## Saidas do SUMO (emission-output)

Para cada veiculo em cada passo de tempo (1 segundo), o SUMO registra:

| Campo       | Unidade  | Descricao                          |
|-------------|----------|------------------------------------|
| CO2         | g/s      | Dioxido de carbono                 |
| CO          | g/s      | Monoxido de carbono                |
| HC          | g/s      | Hidrocarbonetos nao queimados      |
| NOx         | g/s      | Oxidos de nitrogenio               |
| PMx         | g/s      | Material particulado               |
| fuel        | ml/s     | Consumo de combustivel             |
| speed       | m/s      | Velocidade instantanea             |

---

## Modelo de Emissao

O SUMO utiliza o modelo **HBEFA 3.1/3.3** (Handbook Emission Factors for
Road Transport), que calcula emissoes em funcao de:

```
Emissao(t) = f(velocidade(t), aceleracao(t), tipo_veiculo, tipo_via)
```

Para caminhoes pesados a diesel:
- `HBEFA3/HDV_D_EU4` - Euro IV (padrao frota brasileira atual)
- `HBEFA3/HDV_D_EU3` - Euro III (frota mais antiga)

---

## Hipotese de Pesquisa

> "A rota mais curta nao e necessariamente a que menos polui.
>  O congestionamento e as paradas forcadas por semaforos aumentam
>  significativamente as emissoes por acelerar-frear repetidamente,
>  podendo tornar a rota mais longa (rodovia) ambientalmente superior
>  quando analisada por quilometro percorrido."

---

## Resultados Obtidos

### Emissoes por km por veiculo (normalizadas)

| Cenario             | CO2 (g/km) | NOx (g/km) | PMx (g/km) |
|---------------------|------------|------------|------------|
| A - Urbana (EuroIV) | 1.028.255  | 6.685      | 24,3       |
| B - Arterial(EuroIV)| 973.364    | 6.077      | 19,2       |
| C - Rodovia (EuroIV)| 938.646    | 5.638      | 15,3       |
| D - Urbana (EuroIII)| 1.026.185  | 8.203      | 151,0      |

### Conclusoes

- **Por km percorrido**, a rota urbana emite **9,5% mais CO2** que a rodovia,
  confirmando que semaforos e baixa velocidade aumentam emissoes por km.
- Euro III emite **22,7% mais NOx** e **520,7% mais PMx** que Euro IV na mesma rota.
- A renovacao da frota tem impacto ambiental significativo, especialmente
  em material particulado.

---

## Referencias

- SUMO Documentation: https://sumo.dlr.de/docs/
- HBEFA 3.3: https://www.hbefa.net/
- KRAJZEWICZ, D. et al. Recent Development and Applications of SUMO.
  *International Journal On Advances in Systems and Measurements*, 2012.
- Aula 07 - Interfaces / ASMA - Prof. Humberto de Paiva Junior - UFABC, 2023.
