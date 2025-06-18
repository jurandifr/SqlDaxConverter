import re
import sqlparse
from typing import Dict, List, Any
import logging

class SQLParser:
    """Parser for SQL code"""
    
    def __init__(self):
        self.keywords = {
            'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY',
            'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP',
            'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN',
            'UNION', 'INTERSECT', 'EXCEPT'
        }
        
        self.aggregation_functions = {
            'SUM', 'COUNT', 'AVG', 'MIN', 'MAX', 'STDEV', 'VAR',
            'COUNT_BIG', 'GROUPING', 'CHECKSUM_AGG'
        }
    
    def parse(self, sql_code: str) -> Dict[str, Any]:
        """Parse SQL code and extract structure"""
        try:
            # Parse using sqlparse
            parsed = sqlparse.parse(sql_code)
            
            result = {
                'statements': [],
                'objects': self._identify_objects(sql_code),
                'warnings': [],
                'notes': [],
                'parse_errors': []
            }
            
            for statement in parsed:
                if statement.ttype is None:  # Only process statements, not individual tokens
                    stmt_result = self._parse_statement(statement)
                    if stmt_result:
                        result['statements'].append(stmt_result)
            
            # Add validation warnings
            result['warnings'].extend(self._validate_sql(sql_code))
            
            return result
            
        except Exception as e:
            logging.error(f"SQL parsing error: {str(e)}")
            return {
                'statements': [],
                'objects': {},
                'warnings': [],
                'notes': [],
                'parse_errors': [f"Parse error: {str(e)}"]
            }
    
    def _parse_statement(self, statement) -> Dict[str, Any]:
        """Parse individual SQL statement"""
        try:
            statement_str = str(statement).strip()
            
            if not statement_str:
                return None
            
            # Determine statement type
            stmt_type = self._get_statement_type(statement_str)
            
            if stmt_type == 'SELECT':
                return self._parse_select_statement(statement_str, statement)
            elif stmt_type in ['INSERT', 'UPDATE', 'DELETE']:
                return {
                    'type': stmt_type,
                    'original': statement_str,
                    'supported': False,
                    'note': f'{stmt_type} statements are not directly convertible to DAX'
                }
            else:
                return {
                    'type': 'UNKNOWN',
                    'original': statement_str,
                    'supported': False,
                    'note': 'Unsupported statement type'
                }
                
        except Exception as e:
            logging.error(f"Statement parsing error: {str(e)}")
            return {
                'type': 'ERROR',
                'original': str(statement),
                'error': str(e)
            }
    
    def _get_statement_type(self, statement: str) -> str:
        """Determine the type of SQL statement"""
        statement_upper = statement.upper().strip()
        
        if statement_upper.startswith('SELECT'):
            return 'SELECT'
        elif statement_upper.startswith('INSERT'):
            return 'INSERT'
        elif statement_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif statement_upper.startswith('DELETE'):
            return 'DELETE'
        elif statement_upper.startswith('CREATE'):
            return 'CREATE'
        elif statement_upper.startswith('ALTER'):
            return 'ALTER'
        elif statement_upper.startswith('DROP'):
            return 'DROP'
        else:
            return 'UNKNOWN'
    
    def _parse_select_statement(self, statement_str: str, statement) -> Dict[str, Any]:
        """Parse SELECT statement"""
        result = {
            'type': 'SELECT',
            'original': statement_str,
            'select_columns': [],
            'from_tables': [],
            'where_clause': '',
            'group_by': [],
            'having_clause': '',
            'order_by': [],
            'has_aggregation': False,
            'joins': []
        }
        
        try:
            # Extract SELECT columns
            result['select_columns'] = self._extract_select_columns(statement_str)
            
            # Extract FROM tables
            result['from_tables'] = self._extract_from_tables(statement_str)
            
            # Extract WHERE clause
            result['where_clause'] = self._extract_where_clause(statement_str)
            
            # Extract GROUP BY
            result['group_by'] = self._extract_group_by(statement_str)
            
            # Extract HAVING clause
            result['having_clause'] = self._extract_having_clause(statement_str)
            
            # Extract ORDER BY
            result['order_by'] = self._extract_order_by(statement_str)
            
            # Extract JOINs
            result['joins'] = self._extract_joins(statement_str)
            
            # Check for aggregation
            result['has_aggregation'] = self._has_aggregation_functions(statement_str)
            
            return result
            
        except Exception as e:
            logging.error(f"SELECT statement parsing error: {str(e)}")
            result['error'] = str(e)
            return result
    
    def _extract_select_columns(self, statement: str) -> List[Dict[str, Any]]:
        """Extract columns from SELECT clause"""
        columns = []
        
        try:
            # Find SELECT clause
            select_match = re.search(r'SELECT\s+(.*?)\s+FROM', statement, re.IGNORECASE | re.DOTALL)
            if not select_match:
                return columns
            
            select_clause = select_match.group(1)
            
            # Split by commas (simple approach - could be improved)
            column_parts = re.split(r',(?![^()]*\))', select_clause)
            
            for part in column_parts:
                part = part.strip()
                if not part:
                    continue
                
                column_info = self._parse_select_column(part)
                if column_info:
                    columns.append(column_info)
            
            return columns
            
        except Exception as e:
            logging.error(f"Column extraction error: {str(e)}")
            return columns
    
    def _parse_select_column(self, column_expr: str) -> Dict[str, Any]:
        """Parse individual SELECT column expression"""
        column_info = {
            'original': column_expr,
            'column': '',
            'alias': '',
            'is_aggregation': False,
            'function': '',
            'expression': column_expr
        }
        
        try:
            # Check for alias
            alias_match = re.search(r'\s+AS\s+([a-zA-Z_][a-zA-Z0-9_]*)', column_expr, re.IGNORECASE)
            if alias_match:
                column_info['alias'] = alias_match.group(1)
                column_expr = re.sub(r'\s+AS\s+[a-zA-Z_][a-zA-Z0-9_]*', '', column_expr, flags=re.IGNORECASE)
            
            # Check for aggregation functions
            agg_match = re.search(r'(\w+)\s*\(\s*(.+?)\s*\)', column_expr)
            if agg_match:
                function = agg_match.group(1).upper()
                if function in self.aggregation_functions:
                    column_info['is_aggregation'] = True
                    column_info['function'] = function
                    column_info['column'] = agg_match.group(2).strip()
            else:
                # Simple column reference
                column_info['column'] = column_expr.strip()
            
            return column_info
            
        except Exception as e:
            logging.error(f"Column parsing error: {str(e)}")
            return column_info
    
    def _extract_from_tables(self, statement: str) -> List[str]:
        """Extract table names from FROM clause"""
        tables = []
        
        try:
            from_match = re.search(r'FROM\s+([^WHERE^GROUP^ORDER^HAVING^;]+)', statement, re.IGNORECASE)
            if from_match:
                from_clause = from_match.group(1).strip()
                
                # Simple table extraction (could be improved for complex joins)
                table_parts = re.split(r'\s+(?:INNER\s+)?(?:LEFT\s+)?(?:RIGHT\s+)?(?:FULL\s+)?JOIN\s+', from_clause, flags=re.IGNORECASE)
                
                for part in table_parts:
                    # Extract table name (before any alias)
                    table_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)', part)
                    if table_match:
                        tables.append(table_match.group(1))
            
            return tables
            
        except Exception as e:
            logging.error(f"Table extraction error: {str(e)}")
            return tables
    
    def _extract_where_clause(self, statement: str) -> str:
        """Extract WHERE clause"""
        try:
            where_match = re.search(r'WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+HAVING|;|$)', statement, re.IGNORECASE | re.DOTALL)
            if where_match:
                return where_match.group(1).strip()
            return ''
        except Exception as e:
            logging.error(f"WHERE clause extraction error: {str(e)}")
            return ''
    
    def _extract_group_by(self, statement: str) -> List[str]:
        """Extract GROUP BY columns"""
        try:
            group_match = re.search(r'GROUP\s+BY\s+(.+?)(?:\s+HAVING|\s+ORDER\s+BY|;|$)', statement, re.IGNORECASE)
            if group_match:
                group_clause = group_match.group(1).strip()
                return [col.strip() for col in group_clause.split(',')]
            return []
        except Exception as e:
            logging.error(f"GROUP BY extraction error: {str(e)}")
            return []
    
    def _extract_having_clause(self, statement: str) -> str:
        """Extract HAVING clause"""
        try:
            having_match = re.search(r'HAVING\s+(.+?)(?:\s+ORDER\s+BY|;|$)', statement, re.IGNORECASE | re.DOTALL)
            if having_match:
                return having_match.group(1).strip()
            return ''
        except Exception as e:
            logging.error(f"HAVING clause extraction error: {str(e)}")
            return ''
    
    def _extract_order_by(self, statement: str) -> List[str]:
        """Extract ORDER BY columns"""
        try:
            order_match = re.search(r'ORDER\s+BY\s+(.+?)(?:;|$)', statement, re.IGNORECASE)
            if order_match:
                order_clause = order_match.group(1).strip()
                return [col.strip() for col in order_clause.split(',')]
            return []
        except Exception as e:
            logging.error(f"ORDER BY extraction error: {str(e)}")
            return []
    
    def _extract_joins(self, statement: str) -> List[Dict[str, str]]:
        """Extract JOIN information"""
        joins = []
        
        try:
            join_pattern = r'((?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+ON\s+(.+?)(?=\s+(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN|WHERE|GROUP|ORDER|HAVING|;|$)'
            
            for match in re.finditer(join_pattern, statement, re.IGNORECASE):
                joins.append({
                    'type': match.group(1).strip(),
                    'table': match.group(2).strip(),
                    'condition': match.group(3).strip()
                })
            
            return joins
            
        except Exception as e:
            logging.error(f"JOIN extraction error: {str(e)}")
            return joins
    
    def _has_aggregation_functions(self, statement: str) -> bool:
        """Check if statement contains aggregation functions"""
        for func in self.aggregation_functions:
            if re.search(rf'\b{func}\s*\(', statement, re.IGNORECASE):
                return True
        return False
    
    def _identify_objects(self, sql_code: str) -> Dict[str, List[str]]:
        """Identify SQL objects (tables, columns, functions)"""
        objects = {
            'tables': [],
            'columns': [],
            'functions': [],
            'aliases': []
        }
        
        try:
            # Find tables
            table_patterns = [
                r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
                r'JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
                r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
                r'INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
            ]
            
            for pattern in table_patterns:
                matches = re.findall(pattern, sql_code, re.IGNORECASE)
                objects['tables'].extend(matches)
            
            # Find functions
            function_pattern = r'\b([A-Z_][A-Z0-9_]*)\s*\('
            functions = re.findall(function_pattern, sql_code)
            objects['functions'] = list(set(functions))
            
            # Find aliases
            alias_pattern = r'\bAS\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            aliases = re.findall(alias_pattern, sql_code, re.IGNORECASE)
            objects['aliases'] = list(set(aliases))
            
            # Remove duplicates
            objects['tables'] = list(set(objects['tables']))
            
            return objects
            
        except Exception as e:
            logging.error(f"Object identification error: {str(e)}")
            return objects
    
    def _validate_sql(self, sql_code: str) -> List[str]:
        """Validate SQL code and return warnings"""
        warnings = []
        
        try:
            # Check for common issues
            if 'SELECT *' in sql_code.upper():
                warnings.append("SELECT * is not recommended for DAX conversion. Specify explicit columns.")
            
            if re.search(r'\bNULL\b', sql_code, re.IGNORECASE):
                warnings.append("NULL handling differs between SQL and DAX. Review NULL-related logic.")
            
            if re.search(r'\bSUBQUERY\b|\bEXISTS\b|\bIN\s*\(', sql_code, re.IGNORECASE):
                warnings.append("Subqueries require special handling in DAX conversion.")
            
            if re.search(r'\bWITH\b.*\bAS\b', sql_code, re.IGNORECASE):
                warnings.append("CTEs (Common Table Expressions) need to be converted to DAX variables or separate measures.")
            
            return warnings
            
        except Exception as e:
            logging.error(f"SQL validation error: {str(e)}")
            return warnings
