from .base_converter import BaseConverter
from parsers.sql_parser import SQLParser
from typing import Dict, List, Any
import re

class SQLToDaxConverter(BaseConverter):
    """Converter for SQL to DAX"""
    
    def __init__(self):
        super().__init__()
        self.sql_parser = SQLParser()
    
    def _get_data_type_mappings(self) -> Dict[str, str]:
        """SQL to DAX data type mappings"""
        return {
            'varchar': 'TEXT',
            'nvarchar': 'TEXT',
            'char': 'TEXT',
            'nchar': 'TEXT',
            'text': 'TEXT',
            'ntext': 'TEXT',
            'int': 'INTEGER',
            'integer': 'INTEGER',
            'bigint': 'INTEGER',
            'smallint': 'INTEGER',
            'tinyint': 'INTEGER',
            'decimal': 'DECIMAL',
            'numeric': 'DECIMAL',
            'float': 'DOUBLE',
            'real': 'DOUBLE',
            'money': 'CURRENCY',
            'smallmoney': 'CURRENCY',
            'date': 'DATE',
            'datetime': 'DATETIME',
            'datetime2': 'DATETIME',
            'smalldatetime': 'DATETIME',
            'time': 'TIME',
            'timestamp': 'DATETIME',
            'bit': 'BOOLEAN',
            'uniqueidentifier': 'TEXT'
        }
    
    def _get_function_mappings(self) -> Dict[str, str]:
        """SQL to DAX function mappings"""
        return {
            'sum': 'SUM',
            'count': 'COUNT',
            'avg': 'AVERAGE',
            'min': 'MIN',
            'max': 'MAX',
            'len': 'LEN',
            'length': 'LEN',
            'substring': 'MID',
            'substr': 'MID',
            'upper': 'UPPER',
            'lower': 'LOWER',
            'ltrim': 'TRIM',
            'rtrim': 'TRIM',
            'trim': 'TRIM',
            'concat': 'CONCATENATE',
            'coalesce': 'COALESCE',
            'isnull': 'IF',
            'case': 'SWITCH',
            'cast': 'VALUE',
            'convert': 'VALUE',
            'datepart': 'FORMAT',
            'year': 'YEAR',
            'month': 'MONTH',
            'day': 'DAY',
            'getdate': 'NOW',
            'current_timestamp': 'NOW',
            'row_number': 'RANKX',
            'rank': 'RANKX',
            'dense_rank': 'RANKX'
        }
    
    def _get_null_handling_rules(self) -> Dict[str, str]:
        """SQL NULL handling to DAX conversion rules"""
        return {
            r'IS\s+NULL': 'ISBLANK',
            r'IS\s+NOT\s+NULL': 'NOT(ISBLANK',
            r'ISNULL\s*\(([^,]+),([^)]+)\)': r'IF(ISBLANK(\1), \2, \1)',
            r'COALESCE\s*\(([^)]+)\)': r'COALESCE(\1)',
            r'NULLIF\s*\(([^,]+),([^)]+)\)': r'IF(\1 = \2, BLANK(), \1)'
        }
    
    def parse_code(self, code: str) -> Dict[str, Any]:
        """Parse SQL code"""
        return self.sql_parser.parse(code)
    
    def convert_to_dax(self, parsed_code: Dict[str, Any]) -> str:
        """Convert parsed SQL to DAX"""
        try:
            statements = parsed_code.get('statements', [])
            converted_statements = []
            
            for statement in statements:
                if statement['type'] == 'SELECT':
                    dax_statement = self._convert_select_statement(statement)
                    converted_statements.append(dax_statement)
                elif statement['type'] == 'INSERT':
                    # DAX doesn't support INSERT directly
                    converted_statements.append("-- INSERT statements not supported in DAX")
                elif statement['type'] == 'UPDATE':
                    # DAX doesn't support UPDATE directly
                    converted_statements.append("-- UPDATE statements not supported in DAX")
                elif statement['type'] == 'DELETE':
                    # DAX doesn't support DELETE directly
                    converted_statements.append("-- DELETE statements not supported in DAX")
                else:
                    converted_statements.append(f"-- Unsupported statement type: {statement['type']}")
            
            return '\n\n'.join(converted_statements)
            
        except Exception as e:
            raise Exception(f"DAX conversion failed: {str(e)}")
    
    def _convert_select_statement(self, statement: Dict[str, Any]) -> str:
        """Convert SELECT statement to DAX"""
        dax_parts = []
        
        # Handle aggregations and measures
        if statement.get('has_aggregation'):
            return self._convert_to_measure(statement)
        else:
            return self._convert_to_calculated_column(statement)
    
    def _convert_to_measure(self, statement: Dict[str, Any]) -> str:
        """Convert SQL SELECT with aggregation to DAX measure"""
        select_columns = statement.get('select_columns', [])
        from_tables = statement.get('from_tables', [])
        where_clause = statement.get('where_clause', '')
        group_by = statement.get('group_by', [])
        
        measures = []
        
        for column in select_columns:
            if column.get('is_aggregation'):
                function = self.convert_function(column['function'])
                column_name = column['column']
                # Clean column name if it has table prefix
                if '.' in column_name:
                    column_name = column_name.split('.')[-1]
                table_name = from_tables[0] if from_tables else 'Table'
                
                # Build measure
                measure_name = column.get('alias', '').strip()
                if not measure_name:
                    measure_name = f"SUM_{column_name}" if function == "SUM" else f"{function}_{column_name}"
                
                if where_clause:
                    # Convert WHERE clause to FILTER
                    filter_expression = self._convert_where_to_filter(where_clause, table_name)
                    dax_expression = f"{function}({table_name}[{column_name}], {filter_expression})"
                else:
                    dax_expression = f"{function}({table_name}[{column_name}])"
                
                measures.append(f"{measure_name} = {dax_expression}")
        
        return '\n'.join(measures)
    
    def _convert_to_calculated_column(self, statement: Dict[str, Any]) -> str:
        """Convert SQL SELECT without aggregation to DAX calculated column"""
        select_columns = statement.get('select_columns', [])
        from_tables = statement.get('from_tables', [])
        where_clause = statement.get('where_clause', '')
        
        if not select_columns:
            return "-- No columns to convert"
        
        table_name = from_tables[0] if from_tables else 'Table'
        calculations = []
        
        for column in select_columns:
            # Check if it's a complex expression or simple column reference
            if (column.get('expression') and 
                column['expression'] != column.get('column', '') and
                not column.get('is_aggregation')):
                # Handle calculated expressions (when expression differs from column name)
                expression = column['expression']
                expression = self._convert_sql_expression_to_dax(expression, table_name)
                column_name = column.get('alias', 'CalculatedColumn')
                calculations.append(f"{column_name} = {expression}")
            else:
                # Simple column reference - convert to proper DAX reference
                column_name = column['column']
                # Clean column name if it has table prefix
                if '.' in column_name:
                    column_name = column_name.split('.')[-1]
                alias_name = column.get('alias', '').strip()
                if alias_name:
                    calculations.append(f"{alias_name} = {table_name}[{column_name}]")
                else:
                    calculations.append(f"{column_name} = {table_name}[{column_name}]")
        
        return '\n'.join(calculations)
    
    def _convert_where_to_filter(self, where_clause: str, table_name: str) -> str:
        """Convert SQL WHERE clause to DAX FILTER expression"""
        # Basic conversion - this would need more sophisticated parsing
        filter_expr = where_clause
        
        # Convert common patterns
        filter_expr = re.sub(r'\b(\w+)\s*=\s*(.+)', rf'{table_name}[\1] = \2', filter_expr)
        filter_expr = re.sub(r'\b(\w+)\s*>\s*(.+)', rf'{table_name}[\1] > \2', filter_expr)
        filter_expr = re.sub(r'\b(\w+)\s*<\s*(.+)', rf'{table_name}[\1] < \2', filter_expr)
        filter_expr = re.sub(r'\bAND\b', '&&', filter_expr, flags=re.IGNORECASE)
        filter_expr = re.sub(r'\bOR\b', '||', filter_expr, flags=re.IGNORECASE)
        
        # Handle NULL conversions
        filter_expr = self.handle_null_conversion(filter_expr)
        
        return f"FILTER({table_name}, {filter_expr})"
    
    def _convert_sql_expression_to_dax(self, expression: str, table_name: str) -> str:
        """Convert SQL expression to DAX expression"""
        dax_expr = expression
        
        # Convert functions
        for sql_func, dax_func in self.function_mappings.items():
            pattern = rf'\b{sql_func}\s*\('
            replacement = f'{dax_func}('
            dax_expr = re.sub(pattern, replacement, dax_expr, flags=re.IGNORECASE)
        
        # Convert column references to table[column] format
        # Handle table.column or alias.column references first
        table_column_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)\b'
        def replace_table_column(match):
            full_ref = match.group(1)
            parts = full_ref.split('.')
            if len(parts) == 2:
                table_ref, column_ref = parts
                # Use the actual table name instead of alias
                return f'{table_name}[{column_ref}]'
            return full_ref
        
        dax_expr = re.sub(table_column_pattern, replace_table_column, dax_expr)
        
        # Then handle simple column references
        column_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        def replace_column(match):
            column = match.group(1)
            # Don't convert function names, keywords, or literals
            if column.upper() in ['AND', 'OR', 'NOT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 
                                  'TRUE', 'FALSE', 'NULL', 'SUM', 'COUNT', 'AVG', 'MIN', 'MAX',
                                  'DATE', 'TIME', 'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND',
                                  'IS', 'AS', 'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'DISTINCT']:
                return column
            # Don't convert numeric literals
            if column.isdigit():
                return column
            # Don't convert if already in table[column] format
            if '[' in dax_expr and ']' in dax_expr:
                # Check if this column is already converted
                if f'[{column}]' in dax_expr:
                    return column
            return f'{table_name}[{column}]'
        
        dax_expr = re.sub(column_pattern, replace_column, dax_expr)
        
        # Handle NULL conversions
        dax_expr = self.handle_null_conversion(dax_expr)
        
        return dax_expr
