# PDD — Process Definition Document

## Identificação
- Processo: triagem automatizada de ocorrências viárias.
- Sistema: VigiaVia RPA.
- Objetivo: transformar um lote CSV em registros validados, classificados e entregues em JSON para consumo por outro componente.
- Execução: local, sob comando de operador.

## Gatilho e atores
- Gatilho: operador inicia `python -m src.main`.
- Ator humano: prepara o CSV e avalia ocorrências sinalizadas como possíveis duplicadas.
- Robô: lê, valida, compara, classifica, exporta e registra auditoria.
- Componente consumidor: sistema de gestão que lê o JSON de `data/mvp_inbox/`.

## Entradas
CSV com `id`, `data`, `latitude`, `longitude`, `gravidade`, `descricao`.
Dados de demonstração não contêm identificadores pessoais.

## Pré-condições
- Python 3.10+ instalado.
- CSV disponível e com cabeçalho esperado.
- Permissão de leitura na entrada e escrita nas pastas de saída/log.

## Regras e decisões
1. Se o arquivo não existir, encerrar com erro explícito.
2. Se o cabeçalho não contiver todas as colunas obrigatórias, encerrar.
3. Para cada linha: se faltar campo, data não for ISO, coordenadas não forem numéricas/estiverem fora do intervalo ou gravidade for desconhecida, classificar `INVALIDO`.
4. Para cada registro válido, comparar com os registros anteriormente aceitos no lote usando distância Haversine.
5. Distância menor ou igual a 20 m: `POSSIVEL_DUPLICIDADE`, referenciando o primeiro registro; não enviar de novo.
6. Caso contrário, mapear gravidade alta/média/baixa para prioridade ALTA/MEDIA/BAIXA e classificar `PROCESSADO`.
7. Erro isolado de linha é registrado e o lote continua.
8. Após o lote, gerar CSV completo e JSON de integração. Falha de escrita não deve ser apresentada como sucesso.

## Repetição
Laço `for` sobre todas as linhas do CSV. O processamento é item a item e permite que um item inválido não interrompa os demais.

## Saídas
- CSV de resultado com status, prioridade, referência de duplicidade e motivo.
- JSON com envelope de execução e itens processados.
- Log com início, fim, totais e erros.

## Exceções
- Arquivo ausente, arquivo vazio, cabeçalho incorreto, falha de leitura ou escrita.
- Campo ausente, data inválida, coordenada não numérica/fora do intervalo, gravidade desconhecida.
- Possível duplicidade geográfica.
- Exceção inesperada isolada por registro.

## Controles
- Nenhum dado pessoal no dataset de demonstração.
- Log não registra descrição completa.
- Duplicidade é sinalização, não exclusão definitiva.
- Operador revisa casos sinalizados.
- Raio de 20 m é parâmetro acadêmico de demonstração, ajustável conforme calibração do produto.

## Indicadores
- Total de linhas.
- Quantidade processada.
- Quantidade inválida.
- Possíveis duplicidades.
- Erros.
- Quantidade exportada ao arquivo de integração (igual a processados).
