# Roteiro do vídeo demonstrativo (máximo 3 minutos)

**0:00–0:25 — Problema e objetivo**  
Apresentar o VigiaVia, a dificuldade de receber chamados manuais, imprecisos e duplicados e o papel do RPA na triagem.

**0:25–0:50 — Arquitetura e entrada**  
Mostrar o CSV de demonstração e explicar que o projeto é executado localmente, sem dependência do deploy.

**0:50–1:35 — Execução ponta a ponta**  
Executar `python -m src.main`. Mostrar o lote sendo percorrido, os totais e os arquivos gerados.

**1:35–2:05 — Decisões e repetição**  
Abrir o CSV de resultado e mostrar `PROCESSADO`, `INVALIDO` e `POSSIVEL_DUPLICIDADE`, além das prioridades.

**2:05–2:35 — Integração**  
Abrir o JSON em `data/mvp_inbox/` e explicar o contrato de arquivo estruturado destinado ao componente consumidor do MVP. Não afirmar que o MVP real consumiu o arquivo sem demonstrar esse consumo.

**2:35–2:55 — Exceções e auditoria**  
Mostrar log e testes automatizados, incluindo validação de coordenada inválida.

**2:55–3:00 — Encerramento**  
Resumir o benefício operacional e indicar repositório.
