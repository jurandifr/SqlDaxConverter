from abc import ABC, abstractmethod
from typing import Dict, List, Any
import re

class BaseConverter(ABC):
    """Base class for code converters"""
    
    def __init__(self):
        self.data_type_mappings = self._get_data_type_mappings()
        self.function_mappings = self._get_function_mappings()
        self.null_handling_rules = self._get_null_handling_rules()
    
    @abstractmethod
    def _get_data_type_mappings(self) -> Dict[str, str]:
        """Return data type mappings from source to DAX"""
        pass
    
    @abstractmethod
    def _get_function_mappings(self) -> Dict[str, str]:
        """Return function mappings from source to DAX"""
        pass
    
    @abstractmethod
    def _get_null_handling_rules(self) -> Dict[str, str]:
        """Return NULL handling conversion rules"""
        pass
    
    @abstractmethod
    def parse_code(self, code: str) -> Dict[str, Any]:
        """Parse the source code and extract objects"""
        pass
    
    @abstractmethod
    def convert_to_dax(self, parsed_code: Dict[str, Any]) -> str:
        """Convert parsed code to DAX"""
        pass
    
    def convert(self, source_code: str) -> Dict[str, Any]:
        """Main conversion method"""
        try:
            # Parse the source code
            parsed_result = self.parse_code(source_code)
            
            # Convert to DAX
            dax_code = self.convert_to_dax(parsed_result)
            
            return {
                'dax_code': dax_code,
                'objects': parsed_result.get('objects', {}),
                'warnings': parsed_result.get('warnings', []),
                'notes': parsed_result.get('notes', [])
            }
            
        except Exception as e:
            raise Exception(f"Conversion failed: {str(e)}")
    
    def validate(self, source_code: str) -> Dict[str, Any]:
        """Validate source code"""
        try:
            errors = []
            suggestions = []
            
            # Basic validation
            if not source_code.strip():
                errors.append("Code cannot be empty")
                suggestions.append("Enter valid source code")
                return {'valid': False, 'errors': errors, 'suggestions': suggestions}
            
            # Try to parse the code
            try:
                parsed_result = self.parse_code(source_code)
                if parsed_result.get('parse_errors'):
                    errors.extend(parsed_result['parse_errors'])
                    suggestions.extend(parsed_result.get('suggestions', []))
            except Exception as e:
                errors.append(f"Parse error: {str(e)}")
                suggestions.append("Check syntax and formatting")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'suggestions': suggestions
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation failed: {str(e)}"],
                'suggestions': ["Check code syntax and try again"]
            }
    
    def identify_objects(self, code: str) -> Dict[str, List[str]]:
        """Identify tables, columns, and functions in code"""
        objects = {
            'tables': [],
            'columns': [],
            'functions': [],
            'aliases': []
        }
        
        # Basic regex patterns for object identification
        table_pattern = r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        column_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\s*[,\s]|$)'
        function_pattern = r'\b([A-Z_][A-Z0-9_]*)\s*\('
        alias_pattern = r'\bAS\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        
        # Find tables
        tables = re.findall(table_pattern, code, re.IGNORECASE)
        objects['tables'] = list(set(tables))
        
        # Find functions
        functions = re.findall(function_pattern, code)
        objects['functions'] = list(set(functions))
        
        # Find aliases
        aliases = re.findall(alias_pattern, code, re.IGNORECASE)
        objects['aliases'] = list(set(aliases))
        
        return objects
    
    def convert_data_types(self, data_type: str) -> str:
        """Convert data types to DAX equivalents"""
        data_type_lower = data_type.lower()
        return self.data_type_mappings.get(data_type_lower, data_type)
    
    def convert_function(self, function_name: str) -> str:
        """Convert functions to DAX equivalents"""
        function_lower = function_name.lower()
        return self.function_mappings.get(function_lower, function_name)
    
    def handle_null_conversion(self, expression: str) -> str:
        """Apply NULL handling conversion rules"""
        for source_pattern, dax_replacement in self.null_handling_rules.items():
            expression = re.sub(source_pattern, dax_replacement, expression, flags=re.IGNORECASE)
        return expression
