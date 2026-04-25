#!/bin/bash
# Gera a rede viaria a partir dos arquivos de entrada
# Uso: chmod +x rede/gerar_rede.sh && ./rede/gerar_rede.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_DIR="$SCRIPT_DIR/input"
OUTPUT="$SCRIPT_DIR/rede_frete.net.xml"

export SUMO_HOME="${SUMO_HOME:-/usr/share/sumo}"

echo "Gerando rede viaria..."
netconvert \
    --node-files="$INPUT_DIR/nos.nod.xml" \
    --edge-files="$INPUT_DIR/vias.edg.xml" \
    --output-file="$OUTPUT" \
    --no-turnarounds true \
    --tls.default-type static

if [ $? -eq 0 ]; then
    echo "Rede gerada com sucesso: $OUTPUT"
else
    echo "ERRO ao gerar a rede!"
    exit 1
fi
