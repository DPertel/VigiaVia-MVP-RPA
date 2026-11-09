# VigiaVia RPA — Automação Inteligente de Ocorrências Viárias

**FIAP Global Solution 2026.2 · CitizenTech · Robotic Process Automation**  
**Atividade:** Do Processo Manual à Automação Inteligente

## Integrantes
| Integrante | RM |
|---|---:|
| Deivison Pertel | 550803 |
| Eduardo Akira Murata | 98713 |
| Wesley Souza de Oliveira | 97874 |

## 1. Contexto e problema

O VigiaVia é uma proposta CitizenTech de zeladoria inteligente de vias públicas. O problema abordado é a identificação de buracos e danos no pavimento, que pode depender de chamados manuais, lentos, imprecisos e duplicados. A automação deste repositório representa a etapa operacional que organiza os relatos antes de sua disponibilização a um componente de gestão.

Este projeto RPA é **independente para execução local**. Ele utiliza arquivos CSV/JSON de demonstração e não depende do deploy, Docker, Azure ou API do MVP. A saída estruturada em `data/mvp_inbox/` representa a integração por arquivo com outro componente CitizenTech, conforme a alternativa de arquivos estruturados prevista no desafio. A conexão técnica com a API real do MVP não está implementada neste pacote.

## 2. Objetivo

Automatizar o recebimento em lote de ocorrências viárias, validar campos, detectar possíveis duplicidades geográficas, classificar prioridades, produzir arquivos consumíveis por outro componente e registrar auditoria sem armazenar dados pessoais.

## 3. Fluxo resumido

1. Ler `data/input/ocorrencias.csv`.
2. Validar identificador, data, latitude, longitude, gravidade e descrição.
3. Comparar coordenadas com ocorrências válidas anteriores do mesmo lote.
4. Aplicar regra de prioridade.
5. Exportar ocorrências válidas e não duplicadas para `data/mvp_inbox/ocorrencias_<execucao>.json`.
6. Executar o componente consumidor local (`src/mvp_consumer.py`) para ingerir o JSON em SQLite, simulando o recebimento por outro componente CitizenTech.
7. Exportar relatório completo para `data/output/resultado_<execucao>.csv`.
7. Registrar totais e erros em `logs/`.

## 4. Requisitos

- Python 3.10 ou superior.
- Não requer serviços externos nem bibliotecas de terceiros para a execução principal.

## 5. Como executar no Windows (PowerShell)

```powershell
cd vigiavia-rpa
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m src.main
```

Se a política do PowerShell bloquear a ativação, execute sem ativar o ambiente:

```powershell
py -3 -m src.main
```

O arquivo de entrada de demonstração já está em `data/input/ocorrencias.csv`. Para executar novamente, o robô cria uma nova identificação de execução e novos arquivos de saída.

### Consumir o JSON pelo componente CitizenTech local

Após a execução do RPA, copie o caminho do JSON exibido no terminal e execute:

```powershell
py -3 -m src.mvp_consumer data/mvp_inbox/ocorrencias_<execucao>.json
```

O consumidor grava os registros em `data/mvp_consumer.sqlite3` e usa `occurrence_id` como chave única para evitar reingestão. Esse consumidor é uma simulação local de outro componente CitizenTech; não é a API real nem o banco de produção do VigiaVia.

### Executar com outro arquivo

```powershell
py -3 -m src.main --input data/input/meu_lote.csv
```

### Executar testes

```powershell
py -3 -m unittest discover -s tests -v
```

## 6. Regras de negócio

| Regra | Condição | Resultado |
|---|---|---|
| R01 | Campo obrigatório ausente ou inválido | `INVALIDO`; não segue para integração |
| R02 | Gravidade `alta` | Prioridade `ALTA` |
| R03 | Gravidade `media` | Prioridade `MEDIA` |
| R04 | Gravidade `baixa` | Prioridade `BAIXA` |
| R05 | Distância até 20 metros de ocorrência válida anterior | `POSSIVEL_DUPLICIDADE`; não envia novamente ao arquivo de integração |
| R06 | Registro válido, não duplicado | `PROCESSADO`; enviado ao arquivo estruturado |
| R07 | Erro isolado em um registro | Registrar erro e continuar o lote |

**Atenção:** o raio de 20 metros é um parâmetro demonstrativo configurável, não uma regra oficial confirmada do MVP. A detecção sinaliza possível duplicidade; não apaga registros nem substitui validação humana. A gravidade é informada na entrada e não é inferida por IA.

## 7. Entradas e saídas

### CSV de entrada

Cabeçalho obrigatório:

`id,data,latitude,longitude,gravidade,descricao`

Valores de gravidade aceitos: `alta`, `media`, `baixa`. Coordenadas devem estar dentro dos limites geográficos válidos.

### Saídas

- `data/output/resultado_<execucao>.csv`: todos os registros e seus resultados.
- `data/mvp_inbox/ocorrencias_<execucao>.json`: somente registros válidos, não duplicados e classificados; contrato de integração por arquivo.
- `data/mvp_consumer.sqlite3`: base local do componente consumidor demonstrativo, preenchida quando o comando de consumo é executado.
- `logs/rpa_<execucao>.log`: eventos, contagens e falhas sem dados pessoais.

O identificador da execução e os nomes dos arquivos permitem rastrear cada lote.

## 8. Exceções e resiliência

- Arquivo inexistente: erro claro, log e encerramento com código diferente de zero.
- CSV vazio ou sem colunas obrigatórias: erro de estrutura.
- Linha inválida: classifica como inválida, registra o motivo e continua o lote.
- Coordenada fora do intervalo: invalida o registro.
- Duplicidade: sinaliza e evita uma segunda exportação no lote.
- Falha de escrita: exceção é registrada; o processo termina com falha para evitar declarar integração concluída sem arquivo.
- Reexecução: cada execução gera um novo arquivo; em produção, recomenda-se chave de idempotência persistente no componente consumidor.

## 9. Segurança e LGPD

O conjunto demonstrativo não contém nome, telefone, e-mail, placa ou imagem. O robô processa apenas identificador técnico, data, localização aproximada, gravidade e descrição operacional. Não inclua dados pessoais no CSV. Logs não reproduzem a descrição completa nem dados pessoais. O acesso aos arquivos e a política de retenção devem ser definidos pelo operador do MVP. Dados geográficos ainda podem ser sensíveis dependendo do contexto e devem ser tratados com acesso restrito.

## 10. Estrutura

```text
vigiavia-rpa/
├── src/                 # automação Python
├── data/input/          # lote de entrada
├── data/output/         # resultado completo CSV
├── data/mvp_inbox/      # integração demonstrativa por JSON
├── logs/                # auditoria
├── tests/               # testes automatizados
├── docs/                # PDD, BPMN, arquitetura e relatório
├── assets/evidencias/   # inserir capturas reais da execução
└── README.md
```

## 11. Evidências acadêmicas

Antes da entrega:
1. Executar o robô e os testes no computador da equipe.
2. Capturar terminal com execução concluída, arquivos gerados e testes aprovados.
3. Inserir as imagens reais em `assets/evidencias/` e referenciá-las no PDF.
4. Publicar este repositório no GitHub e substituir o link provisório no PDF.
5. Gravar vídeo de até 3 minutos seguindo `docs/roteiro_video.md`.

## 12. Limites da demonstração

Este pacote comprova processamento local e integração por arquivo estruturado. Não comprova chamada à API, gravação no banco ou ingestão real pelo MVP VigiaVia. Para afirmar integração real, o componente consumidor precisa ler o JSON exportado e a equipe deve registrar uma evidência dessa leitura. Não inventar prints ou resultados: as evidências devem ser capturadas durante a execução real.

## Licença

Projeto acadêmico demonstrativo. Definir a licença antes da publicação pública.
