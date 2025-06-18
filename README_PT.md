# Conversor SQL/Spotfire para DAX

## Visão Geral

Uma ferramenta web poderosa que converte consultas SQL e expressões Spotfire para o formato DAX (Data Analysis Expressions) de forma inteligente. Esta aplicação possui recursos avançados de análise, identificação de objetos e fornece orientações claras para conversões bem-sucedidas.

## Recursos

- **Suporte Multi-Linguagem**: Converte tanto expressões SQL quanto Spotfire para DAX
- **Análise Inteligente**: Identifica automaticamente tabelas, colunas, funções e aliases
- **Validação em Tempo Real**: Valida a sintaxe do código antes da conversão
- **Orientação de Erros**: Mensagens de erro claras com sugestões acionáveis
- **Destaque de Sintaxe**: Realce de código para melhor legibilidade
- **Identificação de Objetos**: Exibição visual dos objetos de banco de dados identificados
- **Design Responsivo**: Funciona perfeitamente em desktop e dispositivos móveis

## Conversões Suportadas

### SQL para DAX
- Instruções SELECT → Medidas/Colunas Calculadas DAX
- Funções de agregação (SUM, COUNT, AVG, etc.)
- Cláusulas WHERE → Funções FILTER
- Operações GROUP BY → Agrupamento implícito em medidas
- Operações JOIN → Funções RELATED/RELATEDTABLE
- Tratamento de NULL → Funções BLANK() do DAX

### Spotfire para DAX
- Expressões de agregação com cláusulas OVER
- Expressões condicionais (IF/CASE)
- Referências de colunas [Coluna] → Tabela[Coluna]
- Funções estatísticas
- Funções de data/hora
- Funções de manipulação de texto

## Instalação

### Pré-requisitos
- Python 3.11 ou superior
- Gerenciador de pacotes pip

### Configuração

1. Clone o repositório:
```bash
git clone <url-do-repositório>
cd sql-spotfire-dax-converter
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python main.py
```

4. Abra seu navegador e navegue para `http://localhost:5000`

## Uso

1. **Selecione o Tipo de Conversão**: Escolha entre "SQL para DAX" ou "Spotfire para DAX"
2. **Digite o Código Fonte**: Cole sua consulta SQL ou expressão Spotfire
3. **Valide**: Clique em "Validar" para verificar a sintaxe (opcional)
4. **Converta**: Clique em "Converter para DAX" para gerar a saída
5. **Revise os Resultados**: Verifique o código DAX convertido e os objetos identificados
6. **Copie a Saída**: Use o botão copiar para copiar o código DAX gerado

### Exemplos de Conversões

#### Exemplo SQL
```sql
-- Entrada
SELECT 
    CustomerID,
    SUM(OrderAmount) as TotalAmount,
    COUNT(*) as OrderCount
FROM Orders 
WHERE OrderDate >= '2023-01-01'
GROUP BY CustomerID

-- Saída
TotalAmount = SUM(Orders[OrderAmount], FILTER(Orders, Orders[OrderDate] >= DATE(2023,1,1)))
OrderCount = COUNT(Orders[CustomerID], FILTER(Orders, Orders[OrderDate] >= DATE(2023,1,1)))
```

#### Exemplo Spotfire
```javascript
// Entrada
Sum([Sales]) OVER ([Region])

// Saída
SUM(Table[Sales], FILTER(Table, Table[Region] = EARLIER(Table[Region])))
```

## Arquitetura

### Backend
- **Flask**: Framework web para tratamento HTTP
- **SQLParse**: Análise e parsing de SQL
- **Parsers Customizados**: Análise de expressões Spotfire
- **Conversores Modulares**: Classes de conversão baseadas em herança

### Frontend
- **Bootstrap 5**: Framework UI responsivo com tema escuro
- **JavaScript Vanilla**: Classes ES6 para funcionalidade do lado cliente
- **Prism.js**: Destaque de sintaxe
- **Feather Icons**: Biblioteca de ícones leve

## Configuração

### Variáveis de Ambiente
- `SESSION_SECRET`: Chave secreta da sessão Flask
- `DATABASE_URL`: String de conexão do banco de dados (opcional)

### Desenvolvimento
```bash
export SESSION_SECRET=sua_chave_secreta_aqui
python main.py
```

### Produção
Use um servidor WSGI como Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

## Endpoints da API

### POST /convert
Converte código fonte para formato DAX.

**Corpo da Requisição:**
```json
{
    "source_code": "SELECT * FROM table",
    "conversion_type": "sql_to_dax"
}
```

**Resposta:**
```json
{
    "success": true,
    "converted_code": "código DAX aqui",
    "objects_identified": {
        "tables": ["table"],
        "columns": [],
        "functions": [],
        "aliases": []
    },
    "warnings": [],
    "conversion_notes": []
}
```

### POST /validate
Valida a sintaxe do código fonte.

**Corpo da Requisição:**
```json
{
    "source_code": "SELECT * FROM table",
    "conversion_type": "sql_to_dax"
}
```

**Resposta:**
```json
{
    "valid": true,
    "errors": [],
    "suggestions": []
}
```

## Contribuindo

1. Faça um fork do repositório
2. Crie uma branch de feature
3. Faça suas alterações
4. Adicione testes para nova funcionalidade
5. Envie um pull request

## Licença

Este projeto está licenciado sob a Licença MIT.

## Suporte

Para problemas, perguntas ou solicitações de recursos, por favor crie uma issue no repositório.

---

*Construído com ❤️ para a comunidade Power BI e Analysis Services*