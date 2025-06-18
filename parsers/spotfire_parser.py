import re
from typing import Dict, List, Any
import logging

class SpotfireParser:
    """Parser for Spotfire expressions"""
    
    def __init__(self):
        self.aggregation_functions = {
            'Sum', 'Count', 'CountDistinct', 'Avg', 'Min', 'Max', 'Median',
            'StDev', 'StDevP', 'Var', 'VarP', 'First', 'Last', 'Percentile',
            'Rank', 'DenseRank', 'RowId', 'RowNumber', 'NTile'
        }
        
        self.calculation_functions = {
            'Concatenate', 'Len', 'Left', 'Right', 'Mid', 'Find', 'Substitute',
            'Upper', 'Lower', 'Trim', 'Year', 'Month', 'Day', 'Hour', 'Minute',
            'Second', 'DateAdd', 'DateDiff', 'Now', 'Today', 'WeekDay', 'WeekNum',
            'Quarter', 'Abs', 'Ceiling', 'Floor', 'Round', 'Mod', 'Power', 'Sqrt',
            'Exp', 'Log', 'Log10', 'Sin', 'Cos', 'Tan', 'ASin', 'ACos', 'ATan', 'PI'
        }
        
        self.conditional_keywords = {'If', 'Case', 'When', 'Then', 'Else', 'End'}
    
    def parse(self, spotfire_code: str) -> Dict[str, Any]:
        """Parse Spotfire expression code"""
        try:
            result = {
                'expressions': [],
                'objects': self._identify_objects(spotfire_code),
                'warnings': [],
                'notes': [],
                'parse_errors': []
            }
            
            # Split into individual expressions (by line or semicolon)
            expressions = self._split_expressions(spotfire_code)
            
            for expr in expressions:
                if expr.strip():
                    parsed_expr = self._parse_expression(expr)
                    if parsed_expr:
                        result['expressions'].append(parsed_expr)
            
            # Add validation warnings
            result['warnings'].extend(self._validate_spotfire(spotfire_code))
            
            return result
            
        except Exception as e:
            logging.error(f"Spotfire parsing error: {str(e)}")
            return {
                'expressions': [],
                'objects': {},
                'warnings': [],
                'notes': [],
                'parse_errors': [f"Parse error: {str(e)}"]
            }
    
    def _split_expressions(self, code: str) -> List[str]:
        """Split code into individual expressions"""
        # Split by lines first
        lines = code.split('\n')
        expressions = []
        
        current_expr = ""
        paren_count = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            
            current_expr += " " + line if current_expr else line
            
            # Count parentheses to handle multi-line expressions
            paren_count += line.count('(') - line.count(')')
            
            # If parentheses are balanced, we have a complete expression
            if paren_count == 0:
                expressions.append(current_expr.strip())
                current_expr = ""
        
        # Add any remaining expression
        if current_expr.strip():
            expressions.append(current_expr.strip())
        
        return expressions
    
    def _parse_expression(self, expression: str) -> Dict[str, Any]:
        """Parse individual Spotfire expression"""
        try:
            expr_type = self._determine_expression_type(expression)
            
            if expr_type == 'AGGREGATION':
                return self._parse_aggregation_expression(expression)
            elif expr_type == 'CONDITIONAL':
                return self._parse_conditional_expression(expression)
            elif expr_type == 'CALCULATION':
                return self._parse_calculation_expression(expression)
            else:
                return {
                    'type': 'UNKNOWN',
                    'original': expression,
                    'expression': expression
                }
                
        except Exception as e:
            logging.error(f"Expression parsing error: {str(e)}")
            return {
                'type': 'ERROR',
                'original': expression,
                'error': str(e)
            }
    
    def _determine_expression_type(self, expression: str) -> str:
        """Determine the type of Spotfire expression"""
        # Check for aggregation functions
        for func in self.aggregation_functions:
            if re.search(rf'\b{func}\s*\(', expression, re.IGNORECASE):
                return 'AGGREGATION'
        
        # Check for conditional expressions
        for keyword in self.conditional_keywords:
            if re.search(rf'\b{keyword}\b', expression, re.IGNORECASE):
                return 'CONDITIONAL'
        
        # Default to calculation
        return 'CALCULATION'
    
    def _parse_aggregation_expression(self, expression: str) -> Dict[str, Any]:
        """Parse Spotfire aggregation expression"""
        result = {
            'type': 'AGGREGATION',
            'original': expression,
            'function': '',
            'column': '',
            'table': '',
            'over_clause': '',
            'where_condition': ''
        }
        
        try:
            # Find aggregation function
            agg_match = re.search(r'\b(\w+)\s*\(', expression, re.IGNORECASE)
            if agg_match:
                result['function'] = agg_match.group(1)
            
            # Extract column/expression inside function
            func_content_match = re.search(r'\w+\s*\(([^)]+)\)', expression, re.IGNORECASE)
            if func_content_match:
                content = func_content_match.group(1).strip()
                
                # Check for column reference
                if content.startswith('[') and content.endswith(']'):
                    result['column'] = content[1:-1]  # Remove brackets
                else:
                    result['column'] = content
            
            # Look for OVER clause
            over_match = re.search(r'OVER\s*\(([^)]+)\)', expression, re.IGNORECASE)
            if over_match:
                result['over_clause'] = over_match.group(1)
            
            # Look for WHERE condition (in some Spotfire aggregations)
            where_match = re.search(r'WHERE\s+(.+?)(?:\s+OVER|$)', expression, re.IGNORECASE)
            if where_match:
                result['where_condition'] = where_match.group(1)
            
            return result
            
        except Exception as e:
            logging.error(f"Aggregation parsing error: {str(e)}")
            result['error'] = str(e)
            return result
    
    def _parse_conditional_expression(self, expression: str) -> Dict[str, Any]:
        """Parse Spotfire conditional expression"""
        result = {
            'type': 'CONDITIONAL',
            'original': expression,
            'condition_type': 'IF'
        }
        
        try:
            if re.search(r'\bIf\s*\(', expression, re.IGNORECASE):
                return self._parse_if_expression(expression, result)
            elif re.search(r'\bCase\b', expression, re.IGNORECASE):
                return self._parse_case_expression(expression, result)
            else:
                result['condition_type'] = 'UNKNOWN'
                return result
                
        except Exception as e:
            logging.error(f"Conditional parsing error: {str(e)}")
            result['error'] = str(e)
            return result
    
    def _parse_if_expression(self, expression: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Spotfire IF expression"""
        # Pattern: If(condition, true_value, false_value)
        if_match = re.search(r'If\s*\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\)', expression, re.IGNORECASE)
        if if_match:
            result['condition'] = if_match.group(1).strip()
            result['true_value'] = if_match.group(2).strip()
            result['false_value'] = if_match.group(3).strip()
        
        return result
    
    def _parse_case_expression(self, expression: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Spotfire CASE expression"""
        result['condition_type'] = 'CASE'
        result['cases'] = []
        
        # This is a simplified parser for CASE expressions
        # Real implementation would need more sophisticated parsing
        case_pattern = r'When\s+([^T]+)\s+Then\s+([^W^E]+)'
        cases = re.findall(case_pattern, expression, re.IGNORECASE)
        
        for condition, value in cases:
            result['cases'].append({
                'condition': condition.strip(),
                'value': value.strip()
            })
        
        # Look for ELSE clause
        else_match = re.search(r'Else\s+([^E]+)', expression, re.IGNORECASE)
        if else_match:
            result['default_value'] = else_match.group(1).strip()
        
        return result
    
    def _parse_calculation_expression(self, expression: str) -> Dict[str, Any]:
        """Parse Spotfire calculation expression"""
        return {
            'type': 'CALCULATION',
            'original': expression,
            'expression': expression,
            'table': 'Table'  # Default table name
        }
    
    def _identify_objects(self, spotfire_code: str) -> Dict[str, List[str]]:
        """Identify Spotfire objects (columns, functions)"""
        objects = {
            'tables': [],
            'columns': [],
            'functions': [],
            'aliases': []
        }
        
        try:
            # Find column references [ColumnName]
            column_pattern = r'\[([^\]]+)\]'
            columns = re.findall(column_pattern, spotfire_code)
            objects['columns'] = list(set(columns))
            
            # Find function calls
            function_pattern = r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\('
            functions = re.findall(function_pattern, spotfire_code)
            objects['functions'] = list(set(functions))
            
            # Spotfire typically doesn't have explicit table references in expressions
            # Tables are usually implicit based on the visualization context
            
            return objects
            
        except Exception as e:
            logging.error(f"Object identification error: {str(e)}")
            return objects
    
    def _validate_spotfire(self, spotfire_code: str) -> List[str]:
        """Validate Spotfire code and return warnings"""
        warnings = []
        
        try:
            # Check for common conversion issues
            if re.search(r'\bIsNull\b|\bIsEmpty\b', spotfire_code, re.IGNORECASE):
                warnings.append("NULL/Empty handling differs between Spotfire and DAX. Review null-checking logic.")
            
            if re.search(r'\bOver\s*\(', spotfire_code, re.IGNORECASE):
                warnings.append("OVER clauses require context conversion in DAX. May need FILTER or CALCULATE functions.")
            
            if re.search(r'\bRank\b|\bDenseRank\b|\bRowNumber\b', spotfire_code, re.IGNORECASE):
                warnings.append("Ranking functions need context specification in DAX using RANKX.")
            
            if re.search(r'\bNode\s*\[', spotfire_code, re.IGNORECASE):
                warnings.append("Node references are Spotfire-specific and may not have direct DAX equivalents.")
            
            if re.search(r'\bIntersect\b|\bUnionAll\b', spotfire_code, re.IGNORECASE):
                warnings.append("Set operations require different approaches in DAX.")
            
            return warnings
            
        except Exception as e:
            logging.error(f"Spotfire validation error: {str(e)}")
            return warnings
