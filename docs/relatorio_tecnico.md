# Relatório Técnico — VigiaVia RPA
## FIAP Global Solution 2026.2 — CitizenTech

### 1. Identificação

**Projeto:** VigiaVia RPA — Automação Inteligente de Ocorrências Viárias.

**Instituição:** FIAP.

**Atividade:** Global Solution 2026.2 — CitizenTech — Robotic Process Automation.

**Integrantes:**

| Integrante | RM |
|---|---:|
| Deivison Pertel | 550803 |
| Eduardo Akira Murata | 98713 |
| Wesley Souza de Oliveira | 97874 |

### 2. Problema e contexto

O VigiaVia busca apoiar a zeladoria inteligente de vias públicas, com foco na identificação e organização de ocorrências relacionadas a buracos e danos no pavimento.

Processos manuais de recebimento e triagem podem gerar demora, inconsistências, duplicidade de registros e dificuldade de rastreamento.

O VigiaVia RPA foi desenvolvido para automatizar parte desse processo, organizando os relatos antes de sua disponibilização a um componente de gestão.

### 3. Objetivo e benefícios

O objetivo é automatizar o recebimento e a triagem de ocorrências viárias, reduzindo tarefas repetitivas e melhorando a organização das informações.

Entre os benefícios esperados estão:

- Redução de conferências manuais.
- Padronização da validação dos dados.
- Identificação de possíveis duplicidades.
- Classificação de prioridades.
- Geração automática de relatórios.
- Rastreabilidade das execuções.
- Persistência local dos registros.
- Acompanhamento visual do processamento.

A automação não substitui a avaliação humana dos casos sinalizados.

### 4. Solução desenvolvida

A solução foi implementada em Python e organizada em módulos independentes.

O sistema possui uma interface gráfica construída com Tkinter e um mecanismo de monitoramento contínuo da pasta de entrada.

Quando um novo arquivo CSV é detectado, o sistema aguarda sua estabilização e inicia o processamento.

As ocorrências passam por validação individual, análise geográfica e classificação. Ao final, são produzidos arquivos CSV e JSON, e o componente consumidor local realiza a persistência no SQLite.

### 5. Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Desenvolvimento do RPA |
| Tkinter | Interface gráfica |
| SQLite | Persistência local demonstrativa |
| CSV | Entrada de dados e relatórios |
| JSON | Integração estruturada |
| Logging | Logs e auditoria |
| Unittest | Testes automatizados |
| PowerShell | Execução no Windows |

A execução principal utiliza recursos da biblioteca padrão do Python.

### 6. Arquitetura modular

Os principais módulos são:

- `main.py`: inicialização, monitoramento contínuo e coordenação do fluxo.
- `gui.py`: interface gráfica e apresentação dos eventos.
- `processor.py`: processamento dos lotes e geração de saídas.
- `validator.py`: validação dos registros.
- `deduplication.py`: cálculo de distância e identificação de possíveis duplicidades.
- `priority.py`: classificação de prioridades.
- `mvp_consumer.py`: consumo do JSON e persistência no SQLite.
- `config.py`: parâmetros e caminhos.
- `logger_config.py`: configuração dos logs.

A modularização facilita manutenção, testes e evolução futura.

### 7. Regras de negócio

Os arquivos CSV devem conter:

`id,data,latitude,longitude,gravidade,descricao`

As regras implementadas incluem:

1. Validação dos campos obrigatórios.
2. Verificação de datas e coordenadas.
3. Aceitação das gravidades alta, média e baixa.
4. Classificação de prioridade conforme a gravidade.
5. Cálculo de distância geográfica pelo método de Haversine.
6. Sinalização de possíveis duplicidades em um raio configurado de 20 metros.
7. Continuidade do processamento após erros individuais.
8. Exportação dos registros válidos e não duplicados.
9. Persistência idempotente no SQLite local.

O raio de 20 metros é um parâmetro acadêmico demonstrativo, não uma regra oficial do produto VigiaVia.

### 8. Monitoramento e interface gráfica

A interface Tkinter permite acompanhar:

- Estado do monitoramento.
- Arquivo atualmente processado.
- Etapa atual.
- Progresso do lote.
- Quantidade de registros processados.
- Quantidade de registros inválidos.
- Possíveis duplicidades.
- Erros identificados.
- Eventos e mensagens operacionais.

O monitoramento observa a pasta `data/input/pendentes/` e aguarda novos arquivos CSV.

Após o processamento, os arquivos são encaminhados para as pastas correspondentes.

### 9. Exceções e recuperação

O sistema contempla diferentes situações de erro:

- Arquivo ausente.
- Arquivo vazio ou com cabeçalho incorreto.
- Falha de leitura ou escrita.
- Dados obrigatórios ausentes.
- Data inválida.
- Coordenadas inválidas.
- Gravidade não reconhecida.
- Erros individuais durante o processamento.
- Falhas durante a integração local.

Os erros são registrados e tratados conforme a etapa em que ocorrem.

Possíveis duplicidades são sinalizadas, sem exclusão automática de registros.

### 10. Logs e auditoria

O sistema mantém registros operacionais para permitir rastreamento das execuções.

São registrados eventos como:

- Inicialização e encerramento do monitoramento.
- Detecção e recebimento de arquivos.
- Início e fim de lotes.
- Processamento individual.
- Rejeição de registros.
- Possíveis duplicidades.
- Geração de relatórios.
- Integração SQLite.
- Arquivamento e falhas.

Os logs não devem reproduzir descrições completas nem dados pessoais.

### 11. Integração com o componente local

O RPA gera arquivos JSON estruturados na pasta `data/mvp_inbox/`.

O módulo `src/mvp_consumer.py` consome esses arquivos e persiste os registros em um banco SQLite local.

O consumidor utiliza uma chave única por ocorrência para impedir a reinserção de registros já cadastrados.

Essa arquitetura demonstra uma integração por arquivo estruturado entre dois componentes locais.

**Limitação:** o projeto não realiza chamadas à API real nem grava no banco de produção do MVP VigiaVia. A integração desenvolvida é demonstrativa e local.

### 12. Testes automatizados

A suíte automatizada utiliza `unittest` e possui 12 testes:

| Módulo | Testes |
|---|---:|
| Deduplicação | 3 |
| Consumidor SQLite | 1 |
| Prioridade | 2 |
| Processamento | 1 |
| Validação | 5 |
| **Total** | **12** |

Comando utilizado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Resultado observado:

```text
Ran 12 tests in 0.072s

OK
```

Todos os 12 testes foram aprovados na execução registrada.

### 13. Testes funcionais realizados

#### 13.1 Processamento de lote

Foi utilizado um arquivo com seis ocorrências.

Resultado observado:

| Indicador | Resultado |
|---|---:|
| Total de ocorrências | 6 |
| Processadas | 3 |
| Inválidas | 2 |
| Possíveis duplicidades | 1 |
| Erros de execução | 0 |

A ocorrência BUR-102 foi sinalizada como possível duplicidade de BUR-101, com distância calculada de 1,13 metro.

BUR-105 foi rejeitada por latitude fora do intervalo permitido.

BUR-106 foi rejeitada por gravidade não reconhecida.

#### 13.2 Inserção de novo registro

Foi criado um arquivo de teste contendo a ocorrência BUR-107, com identificador inédito e coordenadas válidas.

Resultado observado:

| Indicador | Resultado |
|---|---:|
| Novos registros | 1 |
| Já cadastrados | 0 |
| Total no banco | 8 |

O teste confirmou a inserção de um novo registro no SQLite local.

### 14. Segurança e LGPD

O conjunto demonstrativo não utiliza nomes, telefones, e-mails, placas ou imagens de cidadãos.

O sistema trabalha com identificadores técnicos, datas, coordenadas, gravidade e descrição operacional.

Recomenda-se:

- Não inserir dados pessoais nos arquivos de entrada.
- Restringir acesso aos dados geográficos.
- Definir políticas de retenção.
- Restringir o acesso ao banco e aos logs.
- Manter revisão humana para casos sinalizados.

### 15. Limitações e trabalhos futuros

A solução demonstra o processamento local e a integração por arquivos estruturados.

Como possibilidades de evolução, destacam-se:

- Integração com a API real do VigiaVia, mediante contrato técnico.
- Conexão com infraestrutura de produção.
- Calibração do raio de duplicidade com dados reais.
- Inclusão de indicadores históricos.
- Evolução do painel de monitoramento.
- Ampliação dos testes de integração e resiliência.
- Integração com serviços externos de gestão de ocorrências.

### 16. Repositório, vídeo e evidências

**GitHub:** inserir URL pública após publicação.

**Vídeo demonstrativo:** inserir URL após gravação.

**Evidências:** adicionar capturas reais em `assets/evidencias/`.

As evidências devem demonstrar a interface gráfica, o processamento de arquivos, os resultados da integração SQLite e os testes automatizados.

### 17. Conclusão

O VigiaVia RPA demonstra a aplicação de automação robótica de processos em uma proposta CitizenTech voltada à zeladoria inteligente de vias públicas.

A solução integra monitoramento de arquivos, validação de dados, análise geográfica, classificação de prioridades, geração de relatórios, persistência local e acompanhamento visual.

Os testes realizados demonstraram o funcionamento dos principais módulos e a capacidade de processar ocorrências válidas, rejeitar registros inválidos, sinalizar possíveis duplicidades e inserir novos registros no SQLite local.

O projeto atende ao objetivo acadêmico de demonstrar como a automação pode contribuir para processos mais organizados, rastreáveis e eficientes.

---

**FIAP Global Solution 2026.2 — CitizenTech**

Projeto acadêmico demonstrativo.