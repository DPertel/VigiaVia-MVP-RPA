# BPMN — Fluxo do processo

Diagrama em Mermaid (também pode ser recriado no Bizagi Modeler/Draw.io para evidência visual):

```mermaid
flowchart TD
    A([Início]) --> B[Operador inicia RPA]
    B --> C[Ler CSV de entrada]
    C --> D{Arquivo e cabeçalho válidos?}
    D -- Não --> E[Registrar falha de execução]
    E --> Z([Fim com erro])
    D -- Sim --> F[Selecionar próxima ocorrência]
    F --> G{Há ocorrência?}
    G -- Não --> X[Gerar CSV, JSON e resumo]
    X --> Y[Registrar totais]
    Y --> Z2([Fim])
    G -- Sim --> H[Validar campos e coordenadas]
    H --> I{Registro válido?}
    I -- Não --> J[Marcar INVALIDO e registrar motivo]
    I -- Sim --> K[Calcular distância para aceitos]
    K --> L{Dentro de 20 m?}
    L -- Sim --> M[Marcar POSSIVEL_DUPLICIDADE]
    L -- Não --> N[Classificar prioridade]
    N --> O[Adicionar à saída de integração]
    J --> P{Próximo registro}
    M --> P
    O --> P
    P --> F
```

## Elementos BPMN
- Evento inicial: operador dispara o processo.
- Tarefa de serviço: leitura, validação, cálculo geográfico, classificação, exportação e logging.
- Gateway exclusivo: arquivo válido, registro válido, duplicidade e continuidade do lote.
- Evento final: lote exportado ou encerrado por falha estrutural.
- Exceção por item: erro isolado é registrado e o loop continua.
