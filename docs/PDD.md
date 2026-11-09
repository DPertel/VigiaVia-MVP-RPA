# PDD — Process Definition Document
## VigiaVia RPA — Triagem Automatizada de Ocorrências Viárias

### 1. Identificação

- **Processo:** Triagem automatizada de ocorrências viárias.
- **Sistema:** VigiaVia RPA.
- **Instituição:** FIAP — Global Solution 2026.2.
- **Área:** CitizenTech — Robotic Process Automation.
- **Objetivo:** Receber lotes de ocorrências viárias, validar informações, identificar possíveis duplicidades, classificar prioridades e encaminhar registros para integração local.
- **Modo de execução:** Monitoramento contínuo com interface gráfica ou execução por terminal.

### 2. Objetivo do processo

Automatizar atividades repetitivas relacionadas à triagem de ocorrências viárias, reduzindo conferências manuais e melhorando a organização, a rastreabilidade e a consistência dos registros.

O RPA processa arquivos CSV, aplica regras de validação, calcula distâncias geográficas, classifica prioridades e produz arquivos estruturados para consumo por outro componente.

### 3. Gatilho e atores

**Gatilho principal:** inicialização do RPA pelo operador.

**Atores envolvidos:**

- **Operador:** inicia o sistema, disponibiliza arquivos CSV e avalia ocorrências sinalizadas como possíveis duplicidades.
- **RPA:** monitora a pasta de entrada, processa os arquivos, valida registros, calcula distâncias, classifica prioridades e gera saídas.
- **Interface gráfica:** apresenta o estado do monitoramento, o andamento do processamento e os indicadores.
- **Consumidor local:** módulo `src/mvp_consumer.py`, responsável por ler o JSON e persistir registros no SQLite demonstrativo.

### 4. Entradas

Arquivos CSV disponibilizados na pasta:

`data/input/pendentes/`

Cabeçalho obrigatório:

`id,data,latitude,longitude,gravidade,descricao`

Os dados de demonstração são sintéticos e não devem conter identificadores pessoais.

### 5. Pré-condições

- Python 3.10 ou superior instalado.
- Ambiente de execução configurado.
- Estrutura de diretórios disponível.
- Permissão de leitura na pasta de entrada.
- Permissão de escrita nas pastas de saída, processamento, erros e logs.
- Arquivo CSV com estrutura esperada.

### 6. Fluxo operacional

1. O operador inicia o VigiaVia RPA.
2. A interface gráfica é aberta, quando utilizada.
3. O monitoramento contínuo é iniciado.
4. O sistema verifica a pasta de arquivos pendentes.
5. Quando um CSV é identificado, o RPA aguarda a estabilização do arquivo.
6. O arquivo é encaminhado ao processamento.
7. Cada ocorrência é validada individualmente.
8. Registros válidos são comparados geograficamente com ocorrências anteriormente aceitas.
9. Possíveis duplicidades são sinalizadas.
10. Registros válidos e não duplicados recebem classificação de prioridade.
11. O sistema gera relatório CSV e arquivo JSON.
12. O consumidor local processa o JSON e registra os novos dados no SQLite.
13. O arquivo original é arquivado na pasta de processados.
14. O RPA retorna ao estado de espera por novos arquivos.

### 7. Regras de negócio e decisões

**R01 — Arquivo inexistente**

Quando o arquivo informado não existe em uma execução pontual, o sistema apresenta erro e registra a falha.

**R02 — Estrutura inválida**

Se o CSV estiver vazio ou não apresentar as colunas obrigatórias, o processamento não deve ser considerado concluído com sucesso.

**R03 — Validação dos registros**

Cada linha deve conter identificador, data, latitude, longitude, gravidade e descrição válidos.

**R04 — Classificação de prioridade**

| Gravidade | Prioridade |
|---|---|
| Alta | ALTA |
| Média | MEDIA |
| Baixa | BAIXA |

**R05 — Detecção de possíveis duplicidades**

O sistema utiliza a fórmula de Haversine para calcular a distância entre coordenadas geográficas.

Quando a distância for menor ou igual a 20 metros em relação a uma ocorrência válida anteriormente aceita, o registro será sinalizado como `POSSIVEL_DUPLICIDADE`.

**R06 — Registro processado**

Quando o registro for válido e não apresentar possível duplicidade, será classificado como `PROCESSADO` e encaminhado ao arquivo JSON.

**R07 — Erro isolado**

Um erro individual deve ser registrado sem interromper desnecessariamente o processamento dos demais registros.

**R08 — Persistência**

O consumidor local utiliza identificador único de ocorrência para impedir reinserção de registros já cadastrados.

**R09 — Arquivamento**

Arquivos processados são encaminhados para `data/processados/`. Arquivos que apresentarem falhas no processamento são encaminhados para `data/erros/`.

### 8. Repetição e controle

O processamento utiliza repetição sobre as linhas do CSV, permitindo análise individual de cada ocorrência.

O monitoramento contínuo verifica periodicamente a pasta de entrada, utilizando o intervalo configurado no projeto.

O encerramento pode ser solicitado pelo operador por meio da interface gráfica ou do terminal.

### 9. Saídas

- **CSV:** relatório detalhado com status, prioridade, referências e motivos de rejeição.
- **JSON:** registros válidos e não duplicados para integração.
- **SQLite:** armazenamento local demonstrativo dos registros consumidos.
- **Logs:** eventos operacionais, auditoria, totais e falhas.
- **Arquivamento:** separação dos arquivos processados e dos arquivos com falhas.

### 10. Exceções

- Arquivo ausente.
- Arquivo vazio.
- Cabeçalho incorreto.
- Falha de leitura ou escrita.
- Campo obrigatório ausente.
- Data inválida.
- Coordenadas não numéricas ou fora dos limites.
- Gravidade desconhecida.
- Possível duplicidade geográfica.
- Erro inesperado durante o processamento ou integração.

### 11. Controles e segurança

- Dataset demonstrativo sem dados pessoais.
- Logs sem reprodução da descrição completa das ocorrências.
- Sinalização de duplicidade sem exclusão automática.
- Revisão humana dos casos sinalizados.
- Raio de 20 metros configurável e utilizado apenas como parâmetro acadêmico.
- Persistência local em SQLite para demonstração.

### 12. Indicadores de desempenho

O sistema apresenta indicadores como:

- Total de ocorrências analisadas.
- Quantidade de registros processados.
- Quantidade de registros inválidos.
- Quantidade de possíveis duplicidades.
- Quantidade de erros.
- Registros novos inseridos no SQLite.
- Registros já cadastrados.
- Total de registros no banco.

### 13. Limitações

A integração demonstrada utiliza JSON e SQLite local. Não representa comunicação com a API real ou com o banco de produção do VigiaVia.

O sistema não utiliza inteligência artificial para inferir gravidade, não realiza análise automática de imagens e não substitui a avaliação humana das ocorrências sinalizadas.

### 14. Resultado esperado

Disponibilizar um processo automatizado, rastreável e modular para triagem de ocorrências viárias, demonstrando a aplicação de RPA em uma solução CitizenTech.