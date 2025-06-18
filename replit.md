# SQL/Spotfire to DAX Converter

## Overview

This is a web-based code conversion tool that transforms SQL queries and Spotfire expressions into DAX (Data Analysis Expressions) format. The application features an intelligent parser that identifies database objects and provides conversion guidance for Power BI and Analysis Services development.

## System Architecture

### Frontend Architecture
- **Framework**: HTML5 with Bootstrap 5 (dark theme)
- **JavaScript**: Vanilla JavaScript with ES6 classes
- **Styling**: Custom CSS with Bootstrap integration
- **Code Highlighting**: Prism.js for syntax highlighting
- **Icons**: Feather Icons for UI elements

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Deployment**: Gunicorn WSGI server
- **Architecture Pattern**: MVC (Model-View-Controller)
- **Code Organization**: Modular converter classes with inheritance hierarchy

## Key Components

### Core Converters
1. **BaseConverter** (`converters/base_converter.py`)
   - Abstract base class defining conversion interface
   - Common functionality for data type mappings and function mappings
   - Template method pattern for conversion workflow

2. **SQLToDaxConverter** (`converters/sql_to_dax.py`)
   - Converts SQL queries to DAX expressions
   - Handles SQL-specific data types and functions
   - Integrates with SQL parser for code analysis

3. **SpotfireToDaxConverter** (`converters/spotfire_to_dax.py`)
   - Converts Spotfire expressions to DAX
   - Handles Spotfire-specific functions and syntax
   - Integrates with Spotfire parser for expression analysis

### Parsers
1. **SQLParser** (`parsers/sql_parser.py`)
   - Uses sqlparse library for SQL code analysis
   - Identifies tables, columns, and SQL constructs
   - Provides validation warnings for SQL code

2. **SpotfireParser** (`parsers/spotfire_parser.py`)
   - Custom parser for Spotfire expression syntax
   - Handles aggregation and calculation functions
   - Identifies conditional logic and expressions

### Web Interface
- **Flask Routes**: RESTful API endpoints for conversion
- **Templates**: Jinja2 templates for responsive UI
- **Static Assets**: CSS and JavaScript for frontend functionality

## Data Flow

1. **Input Processing**
   - User selects conversion type (SQL-to-DAX or Spotfire-to-DAX)
   - Source code entered through web interface
   - Frontend sends AJAX request to Flask backend

2. **Parsing Phase**
   - Appropriate parser analyzes source code structure
   - Identifies database objects (tables, columns, functions)
   - Generates warnings and validation messages

3. **Conversion Phase**
   - Converter applies transformation rules
   - Maps data types and functions to DAX equivalents
   - Handles null values and syntax differences

4. **Output Generation**
   - DAX code generated with proper formatting
   - Object identification results returned
   - Warnings and suggestions provided to user

## External Dependencies

### Python Packages
- **Flask 3.1.1**: Web framework for HTTP handling
- **SQLParse 0.5.3**: SQL parsing and analysis
- **Gunicorn 23.0.0**: Production WSGI server
- **psycopg2-binary 2.9.10**: PostgreSQL adapter (for future database features)

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme
- **Prism.js 1.29.0**: Syntax highlighting for code blocks
- **Feather Icons**: Lightweight icon library

### Infrastructure
- **PostgreSQL**: Database system (configured but not actively used)
- **OpenSSL**: Security and encryption support

## Deployment Strategy

### Development Environment
- **Local Development**: Flask development server with hot reload
- **Debug Mode**: Enabled for development with detailed error messages

### Production Deployment
- **WSGI Server**: Gunicorn with auto-scaling configuration
- **Bind Configuration**: 0.0.0.0:5000 for external access
- **Process Management**: Gunicorn handles worker processes
- **Replit Integration**: Configured for Replit's deployment system

### Configuration
- **Environment Variables**: Session secrets and configuration
- **Logging**: Debug-level logging for development
- **Static Files**: Served through Flask's static file handling

## Changelog

- June 18, 2025: Initial setup - Complete SQL/Spotfire to DAX converter application
- June 18, 2025: Created comprehensive documentation (README.md in English and Portuguese)
- June 18, 2025: Fixed Feather icon compatibility issue
- June 18, 2025: Added dependencies documentation

## User Preferences

- Preferred communication style: Simple, everyday language
- Prefers documentation in both English and Portuguese
- Values comprehensive project documentation