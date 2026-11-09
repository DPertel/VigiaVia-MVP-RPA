# Arquitetura e integração

```text
CSV de entrada
    |
    v
Leitor CSV ---- arquivo ausente/estrutura inválida ---> Log + encerramento
    |
    v
Laço por ocorrência
    |
    v
Validador ---- inválida ---> Resultado INVALIDO + log
    |
    v
Deduplicação geográfica (Haversine, raio demonstrativo de 20 m)
    | duplicada
    +----------------------> POSSIVEL_DUPLICIDADE + referência
    |
    v
Regra de prioridade (alta/média/baixa)
    |
    v
Coleção de itens aprovados
    |
    +----> CSV de auditoria (todos os registros)
    |
    +----> JSON estruturado em data/mvp_inbox/ (itens aprovados)
                         |
                         v
             Consumidor local SQLite (segundo componente demonstrativo)
```

## Contrato de integração por arquivo

O arquivo JSON possui `schema_version`, `execution_id`, `generated_at`, `source` e `items`. Cada item contém `occurrence_id`, `occurred_at`, `latitude`, `longitude`, `severity`, `priority`, `description`, `source` e `execution_id`.

O diretório `data/mvp_inbox/` funciona como área de troca. Um componente consumidor deve ler o JSON e confirmar o recebimento. O pacote inclui `src/mvp_consumer.py`, um segundo componente local que lê o JSON e grava registros em SQLite com chave única por ocorrência (idempotência). Isso demonstra integração por arquivo estruturado entre dois componentes locais. Não é uma conexão com a API/banco de produção do MVP VigiaVia; essa conexão exigiria o contrato real do sistema.

## Idempotência e produção

Cada execução tem identificador único e arquivo próprio. Para implantação real, o consumidor deve manter chave única para `occurrence_id` e `execution_id`, mover arquivos consumidos para uma pasta de processados e aplicar política de reprocessamento/retentativa.
