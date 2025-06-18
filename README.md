# SQL/Spotfire to DAX Converter

## Overview

A powerful web-based tool that intelligently converts SQL queries and Spotfire expressions to DAX (Data Analysis Expressions) format. This application features advanced parsing capabilities, object identification, and provides clear guidance for successful conversions.

## Features

- **Multi-Language Support**: Convert both SQL and Spotfire expressions to DAX
- **Intelligent Parsing**: Automatically identifies tables, columns, functions, and aliases
- **Real-time Validation**: Validates code syntax before conversion
- **Error Guidance**: Clear error messages with actionable suggestions
- **Syntax Highlighting**: Code highlighting for better readability
- **Object Identification**: Visual display of identified database objects
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Supported Conversions

### SQL to DAX
- SELECT statements → DAX Measures/Calculated Columns
- Aggregation functions (SUM, COUNT, AVG, etc.)
- WHERE clauses → FILTER functions
- GROUP BY operations → Implicit grouping in measures
- JOIN operations → RELATED/RELATEDTABLE functions
- NULL handling → DAX BLANK() functions

### Spotfire to DAX
- Aggregation expressions with OVER clauses
- Conditional expressions (IF/CASE)
- Column references [Column] → Table[Column]
- Statistical functions
- Date/time functions
- String manipulation functions

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd sql-spotfire-dax-converter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Select Conversion Type**: Choose between "SQL to DAX" or "Spotfire to DAX"
2. **Enter Source Code**: Paste your SQL query or Spotfire expression
3. **Validate**: Click "Validate" to check syntax (optional)
4. **Convert**: Click "Convert to DAX" to generate the output
5. **Review Results**: Check the converted DAX code and identified objects
6. **Copy Output**: Use the copy button to copy the generated DAX code

### Example Conversions

#### SQL Example
```sql
-- Input
SELECT 
    CustomerID,
    SUM(OrderAmount) as TotalAmount,
    COUNT(*) as OrderCount
FROM Orders 
WHERE OrderDate >= '2023-01-01'
GROUP BY CustomerID

-- Output
TotalAmount = SUM(Orders[OrderAmount], FILTER(Orders, Orders[OrderDate] >= DATE(2023,1,1)))
OrderCount = COUNT(Orders[CustomerID], FILTER(Orders, Orders[OrderDate] >= DATE(2023,1,1)))
```

#### Spotfire Example
```javascript
// Input
Sum([Sales]) OVER ([Region])

// Output
SUM(Table[Sales], FILTER(Table, Table[Region] = EARLIER(Table[Region])))
```

## Architecture

### Backend
- **Flask**: Web framework for HTTP handling
- **SQLParse**: SQL parsing and analysis
- **Custom Parsers**: Spotfire expression parsing
- **Modular Converters**: Inheritance-based conversion classes

### Frontend
- **Bootstrap 5**: Responsive UI framework with dark theme
- **Vanilla JavaScript**: ES6 classes for client-side functionality
- **Prism.js**: Syntax highlighting
- **Feather Icons**: Lightweight icon library

## Configuration

### Environment Variables
- `SESSION_SECRET`: Flask session secret key
- `DATABASE_URL`: Database connection string (optional)

### Development
```bash
export SESSION_SECRET=your_secret_key_here
python main.py
```

### Production
Use a WSGI server like Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

## API Endpoints

### POST /convert
Converts source code to DAX format.

**Request Body:**
```json
{
    "source_code": "SELECT * FROM table",
    "conversion_type": "sql_to_dax"
}
```

**Response:**
```json
{
    "success": true,
    "converted_code": "DAX code here",
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
Validates source code syntax.

**Request Body:**
```json
{
    "source_code": "SELECT * FROM table",
    "conversion_type": "sql_to_dax"
}
```

**Response:**
```json
{
    "valid": true,
    "errors": [],
    "suggestions": []
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or feature requests, please create an issue in the repository.

---

*Built with ❤️ for the Power BI and Analysis Services community*