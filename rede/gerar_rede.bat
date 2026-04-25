@echo off
REM Gera a rede viaria a partir dos arquivos de entrada
REM Uso: clicar duas vezes ou executar no CMD

echo Gerando rede viaria...
netconvert ^
    --node-files=rede\input\nos.nod.xml ^
    --edge-files=rede\input\vias.edg.xml ^
    --output-file=rede\rede_frete.net.xml ^
    --no-turnarounds true ^
    --tls.default-type static

if %ERRORLEVEL% EQU 0 (
    echo Rede gerada com sucesso!
) else (
    echo ERRO ao gerar a rede!
)
pause
