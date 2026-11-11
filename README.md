# 🚧 VigiaVia RPA — Automação Inteligente de Ocorrências Viárias

**FIAP Global Solution 2026.2 · CitizenTech · Robotic Process Automation**

**Atividade:** Do Processo Manual à Automação Inteligente

---

## 👥 Integrantes

| Integrante | RM |
|---|---:|
| Deivison Pertel | 550803 |
| Eduardo Akira Murata | 98713 |
| Wesley Souza de Oliveira | 97874 |

---

## Ficha técnica do MVP

| Item | VigiaVia |
|---|---|
| **Nome do produto** | VigiaVia — zeladoria inteligente de vias públicas |
| **Cidadão e território** | Quem circula pelas vias (motociclistas, ciclistas, pedestres, motoristas, usuários de ônibus) e os agentes de zeladoria das subprefeituras. Piloto: centro de São Paulo (Bela Vista). |
| **Problema, em uma frase** | Buracos nas vias causam acidentes e custos, e sua identificação depende de chamados manuais, lentos, imprecisos e duplicados (113,1 mil pedidos de tapa-buraco em SP em 2025). |
| **Proposta de valor** | Detectar buracos automaticamente com as câmeras que já circulam pela cidade e entregar à zeladoria um relato único, georreferenciado e priorizado por buraco — com privacidade e validação humana. |
| **Arquitetura: componentes** | API FastAPI + interface web (cidadão e zeladoria) · detector YOLO26n em ONNX Runtime · fila de relatos com deduplicação geográfica · Azure Container Apps + ACR + Log Analytics (Terraform) · pipeline DevSecOps (GitHub Actions) · Prometheus + Grafana. |
| **Fontes de dados** | RDD2022 (treino do modelo, CC BY-SA 4.0); relatos e detecções enviados pelos cidadãos; dados de demonstração simulados na Bela Vista (sinalizados como `demonstracao`). |
| **Modelos de IA utilizados** | YOLO26n treinado no RDD2022 (mAP@0,5 = 0,585 no teste), exportado para ONNX; executado no servidor (ONNX Runtime) ou no navegador (onnxruntime-web). |
| **URL do MVP e repositório** | https://ca-vigiavia-prod.happywave-0bf5b4c3.brazilsouth.azurecontainerapps.io · https://github.com/akiramrt/vigiavia-mvp |
| **Indicadores de impacto** | Tempo entre detecção e reparo · % de chamados duplicados evitados · buracos detectados por km rodado · precisão das detecções confirmadas pela zeladoria. Operação: disponibilidade, p95 de latência, taxa de erros e saturação (4 sinais de ouro). |
| **ODS conectados** | **11.2** transporte seguro (reparo mais rápido e alerta ao condutor reduzem quedas de motos e bicicletas) · **11.3** gestão participativa (o cidadão relata e confirma; a fila prioriza o que a população aponta) · **9.1** infraestrutura resiliente (reparo antes de o buraco crescer) · **3.6** menos lesões e mortes no trânsito. Cada meta é acompanhada pelos indicadores acima. |

## 1. 📌 Contexto e problema

O VigiaVia é uma proposta CitizenTech voltada à zeladoria inteligente de vias públicas.

O projeto aborda o problema da identificação e organização de ocorrências viárias, como buracos e danos no pavimento. Processos manuais podem gerar demora no tratamento dos relatos, inconsistências nos dados e registros duplicados.

A solução desenvolvida neste repositório é um **Robotic Process Automation (RPA)** que automatiza o recebimento, a validação, a classificação e o encaminhamento de relatos de ocorrências viárias.

Este pacote é independente e executável localmente. Utiliza arquivos CSV e JSON e um banco SQLite demonstrativo. 

## 2. 🎯 Objetivo

Automatizar o processamento de ocorrências viárias, reduzindo tarefas manuais e melhorando a organização dos registros.

O sistema permite:

- Receber arquivos CSV automaticamente.
- Validar os dados de cada ocorrência.
- Identificar possíveis duplicidades geográficas.
- Classificar prioridades conforme a gravidade informada.
- Gerar relatórios CSV e arquivos JSON.
- Integrar os registros válidos a um banco SQLite local.
- Evitar a reinserção de registros já cadastrados.
- Registrar eventos e resultados para auditoria.
- Acompanhar o processamento por uma interface gráfica.

## 3. ⚙️ Arquitetura e fluxo de funcionamento

O RPA utiliza uma arquitetura modular em Python.

### Fluxo operacional

1. O monitoramento observa a pasta `data/input/pendentes`.
2. Quando um arquivo CSV é identificado, o sistema aguarda sua estabilização.
3. O arquivo é recebido e encaminhado para processamento.
4. Cada ocorrência passa pela validação dos campos obrigatórios.
5. As coordenadas são comparadas com ocorrências válidas para identificar possíveis duplicidades.
6. Os registros válidos recebem uma classificação de prioridade.
7. O sistema gera um relatório CSV e um arquivo JSON.
8. O componente consumidor local recebe o JSON e registra os dados no SQLite.
9. O arquivo original é movido para a pasta de processados.
10. Os eventos e resultados são registrados nos logs.

### Diagrama simplificado

```text
       Arquivo CSV
            |
            v
   Pasta de entrada
       pendentes
            |
            v
   Monitoramento RPA
            |
            v
     Validação dos dados
            |
            v
   Detecção de duplicidades
            |
            v
  Classificação de prioridade
            |
            v
     Geração de arquivos
       /           \
      v             v
 Relatório CSV    Integração JSON
                       |
                       v
                 Consumidor local
                       |
                       v
                   SQLite
                       |
                       v
               Arquivamento CSV
```

## 4. 🧰 Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python 3.10+ | Linguagem principal |
| Tkinter | Interface gráfica |
| SQLite | Armazenamento local demonstrativo |
| CSV | Recebimento e relatórios |
| JSON | Estrutura de integração |
| Logging | Registro de eventos |
| Unittest | Testes automatizados |
| PowerShell | Execução no Windows |

O projeto utiliza recursos da biblioteca padrão do Python, sem dependências externas para sua execução principal.

## 5. 📂 Estrutura do projeto

```text
vigiavia-mvp-rpa/
│
├── assets/
│
├── data/
│   ├── input/
│   │   └── pendentes/
│   ├── output/
│   ├── mvp_inbox/
│   ├── processados/
│   └── erros/
│
├── docs/
│
├── logs/
│
├── src/
│   ├── config.py
│   ├── deduplication.py
│   ├── gui.py
│   ├── logger_config.py
│   ├── main.py
│   ├── mvp_consumer.py
│   ├── priority.py
│   ├── processor.py
│   ├── validator.py
│   └── __init__.py
│
├── tests/
│   ├── test_deduplication.py
│   ├── test_mvp_consumer.py
│   ├── test_priority.py
│   ├── test_processor.py
│   └── test_validator.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

**Responsabilidade dos principais módulos:**

- `main.py`: inicialização, monitoramento contínuo e controle do fluxo.
- `gui.py`: interface gráfica e acompanhamento das atividades.
- `processor.py`: processamento dos lotes e geração de arquivos.
- `validator.py`: validação dos dados recebidos.
- `deduplication.py`: identificação de possíveis duplicidades geográficas.
- `priority.py`: classificação de prioridade.
- `mvp_consumer.py`: consumo do JSON e persistência no SQLite.
- `config.py`: caminhos e parâmetros de configuração.
- `logger_config.py`: configuração dos registros de execução.

## 6. 📋 Formato dos arquivos de entrada

O sistema recebe arquivos CSV com o seguinte cabeçalho obrigatório:

```csv
id,data,latitude,longitude,gravidade,descricao
```

Exemplo:

```csv
id,data,latitude,longitude,gravidade,descricao
BUR-101,2026-11-09,-23.550520,-46.633308,alta,Buraco profundo próximo à faixa de pedestres
BUR-102,2026-11-09,-23.550530,-46.633310,media,Buraco próximo ao primeiro registro
BUR-103,2026-11-09,-23.561000,-46.655000,baixa,Pequena irregularidade no asfalto
```

### Regras de validação

- Identificador obrigatório.
- Data válida.
- Latitude e longitude dentro dos intervalos geográficos permitidos.
- Gravidade reconhecida.
- Descrição obrigatória.

Valores de gravidade aceitos:

- `alta`
- `media`
- `baixa`

## 7. 🧠 Regras de negócio

| Regra | Condição | Resultado |
|---|---|---|
| R01 | Campo obrigatório inválido ou ausente | Registro rejeitado |
| R02 | Gravidade alta | Prioridade ALTA |
| R03 | Gravidade média | Prioridade MEDIA |
| R04 | Gravidade baixa | Prioridade BAIXA |
| R05 | Ocorrência próxima de outra válida | Possível duplicidade |
| R06 | Registro válido e não duplicado | Encaminhado para integração |
| R07 | Erro isolado em um registro | Registrado sem interromper o lote |
| R08 | Registro já existente no SQLite | Não é inserido novamente |

### Detecção de duplicidades

O sistema utiliza a fórmula de Haversine para calcular a distância geográfica entre ocorrências.

O raio configurado para a demonstração é de 20 metros.

A identificação sinaliza uma **possível duplicidade**, não uma duplicidade comprovada. O resultado deve ser interpretado como indicação para análise humana.

A gravidade é informada no arquivo de entrada e não é inferida por inteligência artificial.

## 8. 🖥️ Instalação e execução

### Requisitos

- Windows 10 ou 11.
- Python 3.10 ou superior.
- PowerShell.
- Git, caso deseje clonar o repositório.

### Preparação do ambiente

Clone o repositório e acesse a pasta do projeto:

```powershell
git clone URL_DO_REPOSITORIO
cd vigiavia-mvp-rpa
```

Crie o ambiente virtual:

```powershell
py -3 -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se houver bloqueio de execução do PowerShell, utilize diretamente o executável do ambiente virtual nos comandos abaixo.

### Iniciar o RPA com interface gráfica

```powershell
.\.venv\Scripts\python.exe -m src.main
```

A interface gráfica será aberta e o monitoramento ficará ativo, aguardando novos arquivos CSV.

### Executar somente pelo terminal

```powershell
.\.venv\Scripts\python.exe -m src.main --no-gui
```

### Executar uma vez com arquivo específico

```powershell
.\.venv\Scripts\python.exe -m src.main --once --input data/input/ocorrencias.csv
```

O modo `--once` executa o processamento pontual, sem iniciar a interface gráfica.

### Encerrar o monitoramento

Feche a interface gráfica ou utilize `Ctrl+C` no terminal de execução.

## 9. 🔄 Como testar o recebimento de um novo relato

Com a interface gráfica aberta, utilize um segundo terminal na pasta do projeto.

Crie um arquivo de teste na pasta monitorada:

```powershell
@'
id,data,latitude,longitude,gravidade,descricao
BUR-107,2026-11-09,-23.600000,-46.700000,alta,Buraco profundo em via publica para teste
'@ | .\.venv\Scripts\python.exe -c "import sys; from pathlib import Path; Path('data/input/pendentes/teste_registro_novo.csv').write_text(sys.stdin.read(), encoding='utf-8')"
```

O sistema deverá detectar automaticamente o arquivo e iniciar o processamento.

Após a conclusão, o CSV original será arquivado em `data/processados/`.

## 10. 📊 Arquivos de saída e integração

O sistema gera:

| Caminho | Finalidade |
|---|---|
| `data/output/` | Relatórios CSV |
| `data/mvp_inbox/` | Arquivos JSON de integração |
| Banco SQLite configurado no projeto | Persistência dos registros |
| `data/processados/` | Arquivos CSV concluídos |
| `data/erros/` | Arquivos que falharam no processamento |
| `logs/` | Registros operacionais e auditoria |

Os nomes dos arquivos de saída incluem um identificador de execução para facilitar o rastreamento de cada lote.

### Integração SQLite

O componente consumidor local utiliza o identificador da ocorrência como chave única para impedir a reinserção de registros já cadastrados.

Essa característica implementa idempotência na persistência local.

**Importante:** o SQLite utilizado é demonstrativo. A integração não representa uma conexão direta com o banco de produção ou com a API real do MVP VigiaVia.

## 11. 🧪 Testes automatizados

Para executar os testes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O projeto possui 12 testes automatizados distribuídos entre:

| Módulo | Quantidade |
|---|---:|
| Deduplicação | 3 |
| Consumidor SQLite | 1 |
| Classificação de prioridade | 2 |
| Processamento | 1 |
| Validação | 5 |
| **Total** | **12** |

### Resultado da execução realizada

```text
Ran 12 tests in 0.072s

OK
```

**Resultado: 12 de 12 testes aprovados.**

## 12. ✅ Evidências de funcionamento

Durante os testes funcionais realizados, foram observados os seguintes resultados.

### Teste de processamento em lote

Arquivo com seis ocorrências:

| Resultado | Quantidade |
|---|---:|
| Processadas | 3 |
| Inválidas | 2 |
| Possíveis duplicidades | 1 |
| Erros de execução | 0 |

A ocorrência BUR-102 foi identificada como possível duplicidade de BUR-101, com distância calculada de 1,13 metro.

As ocorrências BUR-105 e BUR-106 foram rejeitadas por problemas de validação.

### Teste de novo cadastro

Foi enviado um relato inédito, identificado como BUR-107.

Resultado da integração:

| Indicador | Resultado |
|---|---:|
| Novos registros inseridos | 1 |
| Registros já cadastrados | 0 |
| Total no banco | 8 |

O resultado confirma a inserção de um novo registro no banco SQLite local.

### Testes automatizados

Todos os 12 testes automatizados foram executados com sucesso.

As capturas de tela da interface e dos resultados devem ser adicionadas à pasta `assets/evidencias/` antes da entrega.

## 13. 🔐 Segurança e LGPD

O conjunto demonstrativo não utiliza nomes, telefones, e-mails ou outros dados pessoais identificáveis.

O processamento é limitado a identificadores técnicos, datas, coordenadas geográficas, gravidade e descrição operacional.

Recomendações:

- Não incluir dados pessoais nos arquivos CSV.
- Restringir o acesso aos arquivos e ao banco de dados.
- Definir políticas de retenção para logs e relatórios.
- Tratar dados de localização com os cuidados necessários.

## 14. ⚠️ Limitações da demonstração

Este projeto demonstra a automação local do processamento de ocorrências viárias.

As funcionalidades implementadas não comprovam:

- Integração direta com a API real do VigiaVia.
- Comunicação com o banco de produção.
- Publicação automática em infraestrutura de nuvem.
- Uso de inteligência artificial para determinar a gravidade das ocorrências.

O componente SQLite é uma simulação local de integração entre sistemas, utilizando arquivos JSON estruturados.

## 15. 🎓 Considerações finais

O VigiaVia RPA demonstra como a automação de processos pode contribuir para a organização e o tratamento de ocorrências viárias.

A solução integra monitoramento de arquivos, validação de dados, análise geográfica, classificação de prioridades, geração de relatórios, persistência local e acompanhamento visual.

O projeto foi desenvolvido como uma demonstração acadêmica da aplicação de RPA em uma proposta CitizenTech, com foco em modularidade, rastreabilidade e confiabilidade do processamento.

---

**FIAP Global Solution 2026.2 — CitizenTech**

Projeto acadêmico demonstrativo.
