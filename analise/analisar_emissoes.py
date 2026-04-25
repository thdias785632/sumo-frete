
import sys
from pathlib import Path
import pandas as pd
from lxml import etree
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

RESULTADOS_DIR = Path(__file__).resolve().parent.parent / "resultados"
ANALISE_DIR = Path(__file__).resolve().parent

CENARIOS = {
    "A": {
        "arquivo": "emissoes_cenario_A.xml",
        "label": "A - Urbana (Euro IV)",
        "cor": "#0066CC",
    },
    "B": {
        "arquivo": "emissoes_cenario_B.xml",
        "label": "B - Arterial (Euro IV)",
        "cor": "#009933",
    },
    "C": {
        "arquivo": "emissoes_cenario_C.xml",
        "label": "C - Rodovia (Euro IV)",
        "cor": "#CC3300",
    },
    "D": {
        "arquivo": "emissoes_cenario_D.xml",
        "label": "D - Urbana (Euro III)",
        "cor": "#9900CC",
    },
}

POLUENTES = ["CO2", "CO", "HC", "NOx", "PMx", "fuel"]
UNIDADES = {
    "CO2": "g",
    "CO": "g",
    "HC": "g",
    "NOx": "g",
    "PMx": "g",
    "fuel": "ml",
}

def ler_emissoes(caminho: Path) -> dict:
    tree = etree.parse(str(caminho))
    root = tree.getroot()

    totais = {p: 0.0 for p in POLUENTES}

    for veiculo in root.iter("vehicle"):
        for p in POLUENTES:
            valor = veiculo.get(p)
            if valor is not None:
                totais[p] += float(valor)

    return totais


def ler_tripinfo(caminho: Path) -> dict:
    tree = etree.parse(str(caminho))
    root = tree.getroot()

    tempos = []
    distancias = []

    for trip in root.iter("tripinfo"):
        dur = trip.get("duration")
        route_len = trip.get("routeLength")
        if dur is not None:
            tempos.append(float(dur))
        if route_len is not None:
            distancias.append(float(route_len))

    return {
        "tempo_medio_s": sum(tempos) / len(tempos) if tempos else 0,
        "distancia_m": distancias[0] if distancias else 0,
        "n_veiculos": len(tempos),
    }


def construir_tabela(dados: dict) -> pd.DataFrame:
    linhas = []
    for cen, info in dados.items():
        dist_km = info["trip"]["distancia_m"] / 1000
        n_veic = info["trip"]["n_veiculos"]
        linha = {"Cenario": CENARIOS[cen]["label"]}
        linha["Distancia (km)"] = round(dist_km, 2)
        linha["Tempo medio (s)"] = round(info["trip"]["tempo_medio_s"], 1)
        linha["Vel. media (km/h)"] = round(
            dist_km / (info["trip"]["tempo_medio_s"] / 3600), 1
        ) if info["trip"]["tempo_medio_s"] > 0 else 0
        for p in POLUENTES:
            un = UNIDADES[p]
            total = info["emissoes"][p]
            linha[f"{p} ({un})"] = round(total, 2)
            if dist_km > 0 and n_veic > 0:
                linha[f"{p}/{un}/km/veic"] = round(total / (dist_km * n_veic), 2)
        linhas.append(linha)

    return pd.DataFrame(linhas)


def gerar_grafico(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Comparativo de Emissoes por Cenario de Frete\n"
        "ESTU024-17 - ASMA / UFABC",
        fontsize=14,
        fontweight="bold",
    )

    cores = [CENARIOS[c]["cor"] for c in CENARIOS]
    labels = df["Cenario"].tolist()

    for ax, poluente, titulo in zip(
        axes, ["CO2 (g)", "NOx (g)"], ["CO\u2082 Total (g)", "NO\u2093 Total (g)"]
    ):
        valores = df[poluente].tolist()
        bars = ax.bar(labels, valores, color=cores, edgecolor="black", linewidth=0.5)
        ax.set_title(titulo, fontsize=12)
        ax.set_ylabel("Emissao total")
        ax.tick_params(axis="x", rotation=25)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

        for bar, val in zip(bars, valores):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:,.1f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    saida = ANALISE_DIR / "grafico_comparativo.png"
    plt.savefig(saida, dpi=150)
    plt.close()
    print(f"\nGrafico salvo em: {saida}")


def gerar_grafico_todos_poluentes(df: pd.DataFrame):
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(
        "Emissoes Detalhadas por Cenario\nESTU024-17 - ASMA / UFABC",
        fontsize=14,
        fontweight="bold",
    )

    cores = [CENARIOS[c]["cor"] for c in CENARIOS]
    labels = df["Cenario"].tolist()

    for ax, poluente in zip(axes.flat, POLUENTES):
        un = UNIDADES[poluente]
        col = f"{poluente} ({un})"
        valores = df[col].tolist()
        bars = ax.bar(labels, valores, color=cores, edgecolor="black", linewidth=0.5)
        ax.set_title(f"{poluente} ({un})", fontsize=11)
        ax.tick_params(axis="x", rotation=25, labelsize=8)
        for bar, val in zip(bars, valores):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:,.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    saida = ANALISE_DIR / "grafico_detalhado.png"
    plt.savefig(saida, dpi=150)
    plt.close()
    print(f"Grafico detalhado salvo em: {saida}")

def main():
    print("=" * 70)
    print("  ANALISE DE EMISSOES - PROJETO FRETE SUMO")
    print("  ESTU024-17 - ASMA / UFABC")
    print("=" * 70)

    dados = {}
    for cen, cfg in CENARIOS.items():
        arq_emissoes = RESULTADOS_DIR / cfg["arquivo"]
        arq_tripinfo = RESULTADOS_DIR / f"tripinfo_cenario_{cen}.xml"

        if not arq_emissoes.exists():
            print(f"\n[AVISO] Arquivo nao encontrado: {arq_emissoes}")
            print(f"        Execute o cenario {cen} antes de rodar esta analise.")
            continue

        emissoes = ler_emissoes(arq_emissoes)
        trip = ler_tripinfo(arq_tripinfo) if arq_tripinfo.exists() else {
            "tempo_medio_s": 0, "distancia_m": 0, "n_veiculos": 0
        }
        dados[cen] = {"emissoes": emissoes, "trip": trip}
        print(f"\n[OK] Cenario {cen}: {cfg['label']}")
        print(f"     Veiculos: {trip['n_veiculos']}, "
              f"Distancia: {trip['distancia_m']/1000:.1f} km, "
              f"Tempo medio: {trip['tempo_medio_s']:.0f} s")

    if not dados:
        print("\nNenhum dado encontrado. Execute os cenarios primeiro.")
        sys.exit(1)

    df = construir_tabela(dados)

    print("\n" + "=" * 70)
    print("  TABELA COMPARATIVA DE EMISSOES")
    print("=" * 70)
    print(df.to_string(index=False))

    csv_path = ANALISE_DIR / "tabela_emissoes.csv"
    df.to_csv(csv_path, index=False, sep=";", decimal=",")
    print(f"\nTabela CSV salva em: {csv_path}")

    gerar_grafico(df)
    gerar_grafico_todos_poluentes(df)

    print("\n" + "=" * 70)
    print("  EMISSOES POR KM POR VEICULO (normalizadas)")
    print("=" * 70)
    cols_por_km = ["Cenario"] + [f"{p}/{UNIDADES[p]}/km/veic" for p in POLUENTES]
    cols_presentes = [c for c in cols_por_km if c in df.columns]
    if len(cols_presentes) > 1:
        print(df[cols_presentes].to_string(index=False))

    print("\n" + "=" * 70)
    print("  CONCLUSAO")
    print("=" * 70)

    if "C" in dados and "A" in dados:
        dist_a = dados["A"]["trip"]["distancia_m"] / 1000
        dist_c = dados["C"]["trip"]["distancia_m"] / 1000
        n_a = dados["A"]["trip"]["n_veiculos"]
        n_c = dados["C"]["trip"]["n_veiculos"]

        co2_urbana = dados["A"]["emissoes"]["CO2"]
        co2_rodovia = dados["C"]["emissoes"]["CO2"]

        co2_km_a = co2_urbana / (dist_a * n_a) if dist_a * n_a > 0 else 0
        co2_km_c = co2_rodovia / (dist_c * n_c) if dist_c * n_c > 0 else 0

        print(f"\n  --- Emissoes TOTAIS (5 caminhoes) ---")
        if co2_rodovia < co2_urbana:
            diff = ((co2_urbana - co2_rodovia) / co2_urbana) * 100
            print(f"  Rodovia (C) emite {diff:.1f}% MENOS CO2 total que Urbana (A).")
        else:
            diff = ((co2_rodovia - co2_urbana) / co2_urbana) * 100
            print(f"  Urbana (A) emite {diff:.1f}% MENOS CO2 total que Rodovia (C).")

        print(f"\n  --- Emissoes POR KM POR VEICULO ---")
        print(f"  CO2/km/veic Urbana  (A): {co2_km_a:,.0f} g")
        print(f"  CO2/km/veic Rodovia (C): {co2_km_c:,.0f} g")
        if co2_km_a > co2_km_c:
            diff_km = ((co2_km_a - co2_km_c) / co2_km_c) * 100
            print(f"  => Urbana emite {diff_km:.1f}% MAIS CO2/km que Rodovia")
            print(f"     (semaforo + baixa velocidade aumentam emissao por km)")
        else:
            diff_km = ((co2_km_c - co2_km_a) / co2_km_a) * 100
            print(f"  => Rodovia emite {diff_km:.1f}% MAIS CO2/km que Urbana")

    if "A" in dados and "D" in dados:
        nox_euroIV = dados["A"]["emissoes"]["NOx"]
        nox_euroIII = dados["D"]["emissoes"]["NOx"]
        pmx_euroIV = dados["A"]["emissoes"]["PMx"]
        pmx_euroIII = dados["D"]["emissoes"]["PMx"]

        print(f"\n  --- Comparacao Euro III vs Euro IV (mesma rota urbana) ---")
        diff_nox = ((nox_euroIII - nox_euroIV) / nox_euroIV) * 100
        diff_pmx = ((pmx_euroIII - pmx_euroIV) / pmx_euroIV) * 100
        print(f"  NOx: Euro III emite {diff_nox:.1f}% mais que Euro IV")
        print(f"  PMx: Euro III emite {diff_pmx:.1f}% mais que Euro IV")
        print(f"  => Frota mais antiga (Euro III) e significativamente mais poluente")
        print(f"     em NOx e material particulado.")

    print()

if __name__ == "__main__":
    main()
