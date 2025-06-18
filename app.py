import os
import logging
from flask import Flask, render_template, request, jsonify, flash
from converters.sql_to_dax import SQLToDaxConverter
from converters.spotfire_to_dax import SpotfireToDaxConverter

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

@app.route('/')
def index():
    """Main page with the conversion interface"""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_code():
    """Convert SQL or Spotfire code to DAX"""
    try:
        data = request.get_json()
        source_code = data.get('source_code', '').strip()
        conversion_type = data.get('conversion_type', 'sql_to_dax')
        
        if not source_code:
            return jsonify({
                'success': False,
                'error': 'Please provide source code to convert',
                'suggestions': ['Enter SQL or Spotfire code in the input area']
            })
        
        # Select appropriate converter
        if conversion_type == 'sql_to_dax':
            converter = SQLToDaxConverter()
        elif conversion_type == 'spotfire_to_dax':
            converter = SpotfireToDaxConverter()
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid conversion type',
                'suggestions': ['Please select either SQL to DAX or Spotfire to DAX']
            })
        
        # Perform conversion
        result = converter.convert(source_code)
        
        return jsonify({
            'success': True,
            'converted_code': result['dax_code'],
            'objects_identified': result['objects'],
            'warnings': result.get('warnings', []),
            'conversion_notes': result.get('notes', [])
        })
        
    except Exception as e:
        logging.error(f"Conversion error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Conversion failed: {str(e)}',
            'suggestions': [
                'Check if your code syntax is valid',
                'Ensure all table and column names are properly formatted',
                'Try converting smaller code segments first'
            ]
        })

@app.route('/validate', methods=['POST'])
def validate_code():
    """Validate source code before conversion"""
    try:
        data = request.get_json()
        source_code = data.get('source_code', '').strip()
        conversion_type = data.get('conversion_type', 'sql_to_dax')
        
        if not source_code:
            return jsonify({
                'valid': False,
                'errors': ['Code cannot be empty'],
                'suggestions': ['Enter SQL or Spotfire code to validate']
            })
        
        # Select appropriate converter for validation
        if conversion_type == 'sql_to_dax':
            converter = SQLToDaxConverter()
        elif conversion_type == 'spotfire_to_dax':
            converter = SpotfireToDaxConverter()
        else:
            return jsonify({
                'valid': False,
                'errors': ['Invalid conversion type'],
                'suggestions': ['Select a valid conversion type']
            })
        
        # Validate the code
        validation_result = converter.validate(source_code)
        
        return jsonify(validation_result)
        
    except Exception as e:
        logging.error(f"Validation error: {str(e)}")
        return jsonify({
            'valid': False,
            'errors': [f'Validation failed: {str(e)}'],
            'suggestions': ['Check code syntax and try again']
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
