# BPMN — Fluxo do Processo VigiaVia RPA

## 1. Descrição

O processo representa o funcionamento do VigiaVia RPA desde sua inicialização até o recebimento, processamento, integração e arquivamento de arquivos CSV.

O monitoramento permanece ativo até que o operador solicite o encerramento.

## 2. Diagrama do processo

O diagrama abaixo utiliza Mermaid como representação visual do fluxo. Para uma entrega que exija notação BPMN formal, recomenda-se reproduzir as tarefas, eventos e gateways no Bizagi Modeler ou Draw.io.

```mermaid
flowchart TD
    A([Início]) --> B[Operador inicia o VigiaVia RPA]
    B --> C[Inicializar interface e monitoramento]
    C --> D[Aguardar arquivo CSV]
    D --> E{Arquivo encontrado?}

    E -- Não --> D
    E -- Sim --> F[Detectar arquivo]
    F --> G[Aguardar estabilização]
    G --> H[Ler arquivo CSV]

    H --> I{Arquivo e cabeçalho válidos?}

    I -- Não --> J[Registrar falha]
    J --> K[Mover arquivo para pasta de erros]
    K --> D

    I -- Sim --> L[Selecionar próxima ocorrência]
    L --> M{Existem registros?}

    M -- Não --> N[Gerar relatório CSV e JSON]
    M -- Sim --> O[Validar campos e coordenadas]

    O --> P{Registro válido?}

    P -- Não --> Q[Marcar como inválido e registrar motivo]
    P -- Sim --> R[Calcular distância geográfica]

    R --> S{Possível duplicidade até 20 m?}

    S -- Sim --> T[Sinalizar possível duplicidade]
    S -- Não --> U[Classificar prioridade]
    U --> V[Adicionar ao JSON de integração]

    Q --> W[Finalizar análise do registro]
    T --> W
    V --> W

    W --> L

    N --> X[Registrar resumo e auditoria]
    X --> Y[Consumir JSON pelo módulo local]
    Y --> Z{Integração concluída?}

    Z -- Sim --> AA[Registrar resultado no SQLite]
    AA --> AB[Arquivar CSV como processado]

    Z -- Não --> AC[Registrar falha de integração]
    AC --> AD[Tratar falha e encaminhar arquivo para erros]

    AB --> AE{Operador encerrou o monitoramento?}
    AD --> AE

    AE -- Não --> D
    AE -- Sim --> AF([Fim])
```

## 3. Elementos do processo

### Eventos

- **Evento inicial:** operador inicia o VigiaVia RPA.
- **Evento intermediário de espera:** monitoramento aguarda novos arquivos.
- **Evento final:** operador encerra o monitoramento.

### Tarefas

- Inicializar interface gráfica.
- Monitorar pasta de entrada.
- Detectar e estabilizar arquivo.
- Ler CSV.
- Validar campos.
- Calcular distância geográfica.
- Classificar prioridade.
- Gerar relatórios.
- Consumir JSON.
- Registrar informações no SQLite.
- Arquivar arquivo original.
- Registrar logs e auditoria.

### Gateways exclusivos

- Arquivo encontrado?
- Arquivo e cabeçalho válidos?
- Existem registros?
- Registro válido?
- Possível duplicidade?
- Integração concluída?
- Operador encerrou o monitoramento?

## 4. Exceções e caminhos alternativos

- Arquivo estruturalmente inválido: registro da falha e encaminhamento para a pasta de erros.
- Registro inválido: rejeição individual e continuidade do lote.
- Possível duplicidade: sinalização sem exclusão automática.
- Falha de integração: registro do erro e tratamento pelo fluxo de exceção.
- Encerramento solicitado: finalização do monitoramento.

## 5. Resultado esperado

O processo automatiza a triagem e a organização de ocorrências viárias, permitindo processamento contínuo de arquivos e integração demonstrativa com um componente local de persistência.