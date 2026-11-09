# Relatório Técnico — VigiaVia RPA

## Identificação
FIAP Global Solution 2026.2 · CitizenTech · Robotic Process Automation  
Integrantes: Deivison Pertel (RM 550803), Eduardo Akira Murata (RM 98713), Wesley Souza de Oliveira (RM 97874).

## Problema e contexto
O VigiaVia busca apoiar a zeladoria inteligente de vias públicas. O projeto CitizenTech aborda buracos que podem ser reportados por chamados manuais, lentos, imprecisos e duplicados. O RPA atua nos bastidores para organizar registros e entregar dados consistentes ao processo de gestão.

## Objetivo e benefício
Automatizar a triagem de ocorrências em lote, reduzir conferências repetitivas, sinalizar possíveis duplicidades e priorizar o atendimento conforme a gravidade informada. O benefício esperado é melhorar a organização e a rastreabilidade, sem substituir a validação humana.

## Processo e tecnologias
O operador fornece CSV. Python lê o lote, valida dados, calcula distância geográfica pelo método Haversine, aplica regras de prioridade, exporta CSV/JSON e gera logs. A execução principal usa biblioteca padrão do Python; testes com `unittest`.

## Regras de negócio
- Campos obrigatórios: id, data, latitude, longitude, gravidade, descrição.
- Gravidade alta/média/baixa gera prioridade ALTA/MEDIA/BAIXA.
- Dados incompletos, datas inválidas, coordenadas fora do intervalo e gravidades desconhecidas são inválidos.
- Distância até 20 m em relação a item previamente aceito gera sinalização de possível duplicidade.
- Erros isolados são registrados e o lote continua.
- O raio de 20 m é parâmetro ilustrativo, não regra oficial do produto.

## Exceções e recuperação
Arquivo ausente ou estrutura inválida interrompe o lote com mensagem e log. Falhas por linha são isoladas. Possíveis duplicidades são sinalizadas, sem exclusão automática. Falha de gravação não é tratada como sucesso.

## Logs e auditoria
Logs registram horário, início/fim, execução, identificadores técnicos, status, prioridade, contagens e tipos de erro. Não registram dados pessoais nem descrição completa. CSV de auditoria mantém o resultado por registro.

## Integração com MVP
O robô produz JSON versionado em `data/mvp_inbox/`. O componente adicional `src/mvp_consumer.py` lê esse arquivo e persiste os registros em SQLite local, com chave única por ocorrência para evitar reingestão. Isso demonstra integração por arquivo estruturado entre o RPA e um segundo componente local CitizenTech. O pacote não chama a API real nem grava no banco de produção do MVP VigiaVia; a conexão real exigiria o contrato de integração do sistema publicado.

## Testes
Testes unitários automatizados cobrem validação, regras de prioridade, distância e processamento em lote. O plano inclui cenários de arquivo ausente e cabeçalho inválido.

## Segurança e LGPD
Dataset sintético sem dados pessoais. Não inserir nomes, telefones, placas, imagens ou identificadores de cidadãos. Restringir acesso a coordenadas e definir retenção conforme política do produto. Revisão humana para casos de duplicidade e prioridade.

## Repositório e vídeo
GitHub: inserir URL pública após publicação.  
Vídeo: inserir URL após gravação.  
Evidências: inserir capturas reais em `assets/evidencias/`.
