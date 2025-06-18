from .base_converter import BaseConverter
from parsers.spotfire_parser import SpotfireParser
from typing import Dict, List, Any
import re

class SpotfireToDaxConverter(BaseConverter):
    """Converter for Spotfire expressions to DAX"""
    
    def __init__(self):
        super().__init__()
        self.spotfire_parser = SpotfireParser()
    
    def _get_data_type_mappings(self) -> Dict[str, str]:
        """Spotfire to DAX data type mappings"""
        return {
            'string': 'TEXT',
            'integer': 'INTEGER',
            'long': 'INTEGER',
            'real': 'DOUBLE',
            'single': 'DOUBLE',
            'double': 'DOUBLE',
            'decimal': 'DECIMAL',
            'datetime': 'DATETIME',
            'date': 'DATE',
            'time': 'TIME',
            'timespan': 'TIME',
            'boolean': 'BOOLEAN',
            'currency': 'CURRENCY'
        }
    
    def _get_function_mappings(self) -> Dict[str, str]:
        """Spotfire to DAX function mappings"""
        return {
            'sum': 'SUM',
            'count': 'COUNT',
            'countdistinct': 'DISTINCTCOUNT',
            'avg': 'AVERAGE',
            'min': 'MIN',
            'max': 'MAX',
            'median': 'MEDIAN',
            'stdev': 'STDEV.S',
            'stdevp': 'STDEV.P',
            'var': 'VAR.S',
            'varp': 'VAR.P',
            'first': 'FIRSTNONBLANK',
            'last': 'LASTNONBLANK',
            'concatenate': 'CONCATENATE',
            'len': 'LEN',
            'left': 'LEFT',
            'right': 'RIGHT',
            'mid': 'MID',
            'find': 'FIND',
            'substitute': 'SUBSTITUTE',
            'upper': 'UPPER',
            'lower': 'LOWER',
            'trim': 'TRIM',
            'if': 'IF',
            'case': 'SWITCH',
            'when': 'SWITCH',
            'year': 'YEAR',
            'month': 'MONTH',
            'day': 'DAY',
            'hour': 'HOUR',
            'minute': 'MINUTE',
            'second': 'SECOND',
            'dateadd': 'DATEADD',
            'datediff': 'DATEDIFF',
            'now': 'NOW',
            'today': 'TODAY',
            'weekday': 'WEEKDAY',
            'weeknum': 'WEEKNUM',
            'quarter': 'QUARTER',
            'abs': 'ABS',
            'ceiling': 'CEILING',
            'floor': 'FLOOR',
            'round': 'ROUND',
            'mod': 'MOD',
            'power': 'POWER',
            'sqrt': 'SQRT',
            'exp': 'EXP',
            'log': 'LOG',
            'log10': 'LOG10',
            'sin': 'SIN',
            'cos': 'COS',
            'tan': 'TAN',
            'asin': 'ASIN',
            'acos': 'ACOS',
            'atan': 'ATAN',
            'pi': 'PI',
            'rank': 'RANKX',
            'densrank': 'RANKX',
            'rowid': 'RANKX',
            'rownumber': 'RANKX',
            'percentile': 'PERCENTILE.EXC',
            'ntile': 'RANKX'
        }
    
    def _get_null_handling_rules(self) -> Dict[str, str]:
        """Spotfire NULL handling to DAX conversion rules"""
        return {
            r'IsNull\s*\(([^)]+)\)': r'ISBLANK(\1)',
            r'IsEmpty\s*\(([^)]+)\)': r'ISBLANK(\1)',
            r'IfNull\s*\(([^,]+),([^)]+)\)': r'IF(ISBLANK(\1), \2, \1)',
            r'NullIf\s*\(([^,]+),([^)]+)\)': r'IF(\1 = \2, BLANK(), \1)',
            r'Coalesce\s*\(([^)]+)\)': r'COALESCE(\1)'
        }
    
    def parse_code(self, code: str) -> Dict[str, Any]:
        """Parse Spotfire expression code"""
        return self.spotfire_parser.parse(code)
    
    def convert_to_dax(self, parsed_code: Dict[str, Any]) -> str:
        """Convert parsed Spotfire expression to DAX"""
        try:
            expressions = parsed_code.get('expressions', [])
            converted_expressions = []
            
            for expr in expressions:
                if expr['type'] == 'AGGREGATION':
                    dax_expr = self._convert_aggregation_expression(expr)
                    converted_expressions.append(dax_expr)
                elif expr['type'] == 'CALCULATION':
                    dax_expr = self._convert_calculation_expression(expr)
                    converted_expressions.append(dax_expr)
                elif expr['type'] == 'CONDITIONAL':
                    dax_expr = self._convert_conditional_expression(expr)
                    converted_expressions.append(dax_expr)
                else:
                    converted_expressions.append(f"-- Unsupported expression type: {expr['type']}")
            
            return '\n\n'.join(converted_expressions)
            
        except Exception as e:
            raise Exception(f"DAX conversion failed: {str(e)}")
    
    def _convert_aggregation_expression(self, expr: Dict[str, Any]) -> str:
        """Convert Spotfire aggregation to DAX measure"""
        function = self.convert_function(expr['function'])
        column = expr['column']
        table = expr.get('table', 'Table')
        
        # Handle aggregation context
        over_clause = expr.get('over_clause', '')
        if over_clause:
            # Convert OVER clause to appropriate DAX context
            context_expr = self._convert_over_clause_to_context(over_clause, table)
            if context_expr:
                return f"{function}({table}[{column}], {context_expr})"
        
        # Handle WHERE conditions in aggregation
        where_condition = expr.get('where_condition', '')
        if where_condition:
            filter_expr = self._convert_spotfire_condition_to_filter(where_condition, table)
            return f"{function}({table}[{column}], {filter_expr})"
        
        return f"{function}({table}[{column}])"
    
    def _convert_calculation_expression(self, expr: Dict[str, Any]) -> str:
        """Convert Spotfire calculation to DAX calculated column"""
        expression = expr['expression']
        table = expr.get('table', 'Table')
        
        # Convert the expression
        dax_expr = self._convert_spotfire_expression_to_dax(expression, table)
        
        return dax_expr
    
    def _convert_conditional_expression(self, expr: Dict[str, Any]) -> str:
        """Convert Spotfire conditional expression to DAX"""
        condition_type = expr.get('condition_type', 'IF')
        
        if condition_type.upper() == 'IF':
            condition = expr['condition']
            true_value = expr['true_value']
            false_value = expr.get('false_value', 'BLANK()')
            table = expr.get('table', 'Table')
            
            # Convert condition and values
            dax_condition = self._convert_spotfire_expression_to_dax(condition, table)
            dax_true = self._convert_spotfire_expression_to_dax(true_value, table)
            dax_false = self._convert_spotfire_expression_to_dax(false_value, table)
            
            return f"IF({dax_condition}, {dax_true}, {dax_false})"
        
        elif condition_type.upper() == 'CASE':
            return self._convert_case_expression(expr)
        
        return "-- Unsupported conditional type"
    
    def _convert_case_expression(self, expr: Dict[str, Any]) -> str:
        """Convert Spotfire CASE expression to DAX SWITCH"""
        cases = expr.get('cases', [])
        table = expr.get('table', 'Table')
        
        if not cases:
            return "BLANK()"
        
        # Build SWITCH expression
        switch_parts = []
        
        for case in cases:
            condition = self._convert_spotfire_expression_to_dax(case['condition'], table)
            value = self._convert_spotfire_expression_to_dax(case['value'], table)
            switch_parts.extend([condition, value])
        
        # Add default case if exists
        default_value = expr.get('default_value')
        if default_value:
            default_dax = self._convert_spotfire_expression_to_dax(default_value, table)
            switch_parts.append(default_dax)
        else:
            switch_parts.append('BLANK()')
        
        return f"SWITCH(TRUE(), {', '.join(switch_parts)})"
    
    def _convert_over_clause_to_context(self, over_clause: str, table: str) -> str:
        """Convert Spotfire OVER clause to DAX context"""
        # This is a simplified conversion - real implementation would need more parsing
        if 'PARTITION BY' in over_clause.upper():
            # Extract partition columns
            partition_match = re.search(r'PARTITION\s+BY\s+(.+?)(?:\s+ORDER\s+BY|$)', over_clause, re.IGNORECASE)
            if partition_match:
                partition_cols = partition_match.group(1).split(',')
                partition_cols = [col.strip() for col in partition_cols]
                filter_conditions = [f"{table}[{col}] = EARLIER({table}[{col}])" for col in partition_cols]
                return f"FILTER({table}, {' && '.join(filter_conditions)})"
        
        return ""
    
    def _convert_spotfire_condition_to_filter(self, condition: str, table: str) -> str:
        """Convert Spotfire condition to DAX FILTER expression"""
        dax_condition = self._convert_spotfire_expression_to_dax(condition, table)
        return f"FILTER({table}, {dax_condition})"
    
    def _convert_spotfire_expression_to_dax(self, expression: str, table: str) -> str:
        """Convert Spotfire expression to DAX expression"""
        if not expression or expression == 'BLANK()':
            return expression
            
        dax_expr = expression
        
        # Convert functions
        for spotfire_func, dax_func in self.function_mappings.items():
            pattern = rf'\b{spotfire_func}\s*\('
            replacement = f'{dax_func}('
            dax_expr = re.sub(pattern, replacement, dax_expr, flags=re.IGNORECASE)
        
        # Convert column references - Spotfire uses [Column] format
        # Convert to Table[Column] format
        column_pattern = r'\[([^\]]+)\]'
        def replace_column(match):
            column = match.group(1)
            return f'{table}[{column}]'
        
        dax_expr = re.sub(column_pattern, replace_column, dax_expr)
        
        # Handle NULL conversions
        dax_expr = self.handle_null_conversion(dax_expr)
        
        # Convert operators
        dax_expr = re.sub(r'\band\b', '&&', dax_expr, flags=re.IGNORECASE)
        dax_expr = re.sub(r'\bor\b', '||', dax_expr, flags=re.IGNORECASE)
        dax_expr = re.sub(r'\bnot\b', 'NOT', dax_expr, flags=re.IGNORECASE)
        
        return dax_expr
