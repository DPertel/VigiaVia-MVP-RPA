# Plano de testes e evidências

Execute: `python -m unittest discover -s tests -v`

| ID | Cenário | Resultado esperado |
|---|---|---|
| T01 | Registro completo e válido | `PROCESSADO` |
| T02 | Campo obrigatório ausente | `INVALIDO` |
| T03 | Latitude fora do intervalo | `INVALIDO` |
| T04 | Data em formato inválido | `INVALIDO` |
| T05 | Gravidade desconhecida | `INVALIDO` |
| T06 | Ponto a até 20 m de item aceito | `POSSIVEL_DUPLICIDADE` |
| T07 | Ponto distante | processado normalmente |
| T08 | Arquivo inexistente | erro explícito e retorno diferente de zero |
| T09 | CSV sem colunas obrigatórias | erro explícito |
| T10 | Lote misto | válidos continuam mesmo com inválidos |

Os testes automatizados incluídos cobrem validação, prioridade, cálculo geográfico e processamento de lote. T08/T09 podem ser executados manualmente ou ampliados com testes de integração. Guardar captura real do terminal em `assets/evidencias/`.

| T11 | Consumir o JSON no componente SQLite | inserir registros e não duplicar em reexecução |
