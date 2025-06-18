// SQL/Spotfire to DAX Converter - Frontend JavaScript

class ConverterApp {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupTooltips();
        this.initializeCodeHighlighting();
    }

    bindEvents() {
        // Button event listeners
        document.getElementById('convertBtn').addEventListener('click', () => this.convertCode());
        document.getElementById('validateBtn').addEventListener('click', () => this.validateCode());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearAll());
        document.getElementById('copyBtn').addEventListener('click', () => this.copyOutput());

        // Real-time validation on input change
        document.getElementById('sourceCode').addEventListener('input', () => this.debounceValidate());

        // Conversion type change
        document.querySelectorAll('input[name="conversionType"]').forEach(radio => {
            radio.addEventListener('change', () => this.updatePlaceholder());
        });

        // Auto-resize textarea
        document.getElementById('sourceCode').addEventListener('input', this.autoResizeTextarea);
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips if needed
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initializeCodeHighlighting() {
        // Initialize Prism.js for syntax highlighting
        if (typeof Prism !== 'undefined') {
            Prism.highlightAll();
        }
    }

    updatePlaceholder() {
        const sourceCode = document.getElementById('sourceCode');
        const conversionType = document.querySelector('input[name="conversionType"]:checked').value;
        
        if (conversionType === 'sql_to_dax') {
            sourceCode.placeholder = `Paste your SQL query here...

Example:
SELECT 
    CustomerID,
    SUM(OrderAmount) as TotalAmount,
    COUNT(*) as OrderCount
FROM Orders 
WHERE OrderDate >= '2023-01-01'
GROUP BY CustomerID`;
        } else {
            sourceCode.placeholder = `Paste your Spotfire expression here...

Examples:
Sum([Sales]) OVER ([Region])
If([Category] = 'Electronics', [Sales] * 1.1, [Sales])
Case When [Status] = 'Active' Then [Value] Else 0 End`;
        }
    }

    debounceValidate() {
        clearTimeout(this.validateTimeout);
        this.validateTimeout = setTimeout(() => {
            const sourceCode = document.getElementById('sourceCode').value.trim();
            if (sourceCode) {
                this.validateCode(true); // Silent validation
            }
        }, 1500);
    }

    autoResizeTextarea(event) {
        const textarea = event.target;
        textarea.style.height = 'auto';
        textarea.style.height = Math.max(200, textarea.scrollHeight) + 'px';
    }

    async convertCode() {
        const sourceCode = document.getElementById('sourceCode').value.trim();
        const conversionType = document.querySelector('input[name="conversionType"]:checked').value;

        if (!sourceCode) {
            this.showError('Please enter source code to convert.');
            return;
        }

        this.showLoading(true);
        this.clearMessages();

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source_code: sourceCode,
                    conversion_type: conversionType
                })
            });

            const result = await response.json();

            if (result.success) {
                this.displayConversionResult(result);
                this.showSuccess('Code converted successfully!');
            } else {
                this.showError(result.error, result.suggestions);
            }

        } catch (error) {
            console.error('Conversion error:', error);
            this.showError('Failed to convert code. Please check your connection and try again.');
        } finally {
            this.showLoading(false);
        }
    }

    async validateCode(silent = false) {
        const sourceCode = document.getElementById('sourceCode').value.trim();
        const conversionType = document.querySelector('input[name="conversionType"]:checked').value;

        if (!sourceCode) {
            if (!silent) {
                this.showError('Please enter source code to validate.');
            }
            return;
        }

        if (!silent) {
            this.showLoading(true);
            this.clearMessages();
        }

        try {
            const response = await fetch('/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source_code: sourceCode,
                    conversion_type: conversionType
                })
            });

            const result = await response.json();

            if (result.valid) {
                if (!silent) {
                    this.showSuccess('Code validation passed!');
                }
            } else {
                this.showError('Validation failed', result.suggestions);
                this.displayErrors(result.errors);
            }

        } catch (error) {
            console.error('Validation error:', error);
            if (!silent) {
                this.showError('Failed to validate code. Please check your connection and try again.');
            }
        } finally {
            if (!silent) {
                this.showLoading(false);
            }
        }
    }

    displayConversionResult(result) {
        // Display DAX output
        this.displayDaxOutput(result.converted_code);
        
        // Display identified objects
        this.displayObjects(result.objects_identified);
        
        // Display warnings and notes
        if (result.warnings && result.warnings.length > 0) {
            this.showWarnings(result.warnings);
        }
        
        if (result.conversion_notes && result.conversion_notes.length > 0) {
            this.showNotes(result.conversion_notes);
        }
    }

    displayDaxOutput(daxCode) {
        const emptyState = document.getElementById('emptyState');
        const daxOutput = document.getElementById('daxOutput');
        const copyBtn = document.getElementById('copyBtn');

        // Hide empty state and show output
        emptyState.style.display = 'none';
        daxOutput.style.display = 'block';
        copyBtn.style.display = 'inline-block';

        // Set the DAX code
        const codeElement = daxOutput.querySelector('code');
        codeElement.textContent = daxCode;

        // Apply syntax highlighting
        if (typeof Prism !== 'undefined') {
            Prism.highlightElement(codeElement);
        }
    }

    displayObjects(objects) {
        this.updateObjectList('tablesList', objects.tables, 'table');
        this.updateObjectList('columnsList', objects.columns, 'column');
        this.updateObjectList('functionsList', objects.functions, 'function');
        this.updateObjectList('aliasesList', objects.aliases, 'alias');
    }

    updateObjectList(listId, items, type) {
        const list = document.getElementById(listId);
        list.innerHTML = '';

        if (items && items.length > 0) {
            items.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<span class="object-badge ${type}">${this.escapeHtml(item)}</span>`;
                list.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.className = 'text-muted';
            li.textContent = `No ${type}s identified`;
            list.appendChild(li);
        }
    }

    showLoading(show) {
        const loadingState = document.getElementById('loadingState');
        const outputContainer = document.getElementById('outputContainer');
        
        if (show) {
            loadingState.style.display = 'block';
            outputContainer.style.display = 'none';
        } else {
            loadingState.style.display = 'none';
            outputContainer.style.display = 'block';
        }
    }

    showSuccess(message) {
        this.hideNoMessages();
        const container = document.getElementById('successMessages');
        container.innerHTML = this.createAlert('success', message, 'check-circle');
        container.style.display = 'block';
    }

    showError(message, suggestions = []) {
        this.hideNoMessages();
        const container = document.getElementById('errorMessages');
        
        let alertContent = `<strong>Error:</strong> ${this.escapeHtml(message)}`;
        
        if (suggestions && suggestions.length > 0) {
            alertContent += '<br><small><strong>Suggestions:</strong></small><ul class="mb-0 mt-1">';
            suggestions.forEach(suggestion => {
                alertContent += `<li><small>${this.escapeHtml(suggestion)}</small></li>`;
            });
            alertContent += '</ul>';
        }
        
        container.innerHTML = this.createAlert('danger', alertContent, 'alert-circle');
        container.style.display = 'block';
    }

    showWarnings(warnings) {
        this.hideNoMessages();
        const container = document.getElementById('warningMessages');
        
        let alertContent = '<strong>Conversion Warnings:</strong><ul class="mb-0 mt-1">';
        warnings.forEach(warning => {
            alertContent += `<li><small>${this.escapeHtml(warning)}</small></li>`;
        });
        alertContent += '</ul>';
        
        container.innerHTML = this.createAlert('warning', alertContent, 'alert-triangle');
        container.style.display = 'block';
    }

    showNotes(notes) {
        this.hideNoMessages();
        const container = document.getElementById('notesMessages');
        
        let alertContent = '<strong>Conversion Notes:</strong><ul class="mb-0 mt-1">';
        notes.forEach(note => {
            alertContent += `<li><small>${this.escapeHtml(note)}</small></li>`;
        });
        alertContent += '</ul>';
        
        container.innerHTML = this.createAlert('info', alertContent, 'info');
        container.style.display = 'block';
    }

    displayErrors(errors) {
        if (errors && errors.length > 0) {
            errors.forEach(error => {
                this.showError(error);
            });
        }
    }

    createAlert(type, content, icon) {
        return `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i data-feather="${icon}" class="me-2"></i>
                ${content}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }

    hideNoMessages() {
        document.getElementById('noMessages').style.display = 'none';
    }

    clearMessages() {
        document.getElementById('successMessages').style.display = 'none';
        document.getElementById('warningMessages').style.display = 'none';
        document.getElementById('errorMessages').style.display = 'none';
        document.getElementById('notesMessages').style.display = 'none';
        document.getElementById('noMessages').style.display = 'block';
    }

    clearAll() {
        // Clear input
        document.getElementById('sourceCode').value = '';
        
        // Clear output
        const emptyState = document.getElementById('emptyState');
        const daxOutput = document.getElementById('daxOutput');
        const copyBtn = document.getElementById('copyBtn');
        
        emptyState.style.display = 'block';
        daxOutput.style.display = 'none';
        copyBtn.style.display = 'none';
        
        // Clear objects
        this.updateObjectList('tablesList', [], 'table');
        this.updateObjectList('columnsList', [], 'column');
        this.updateObjectList('functionsList', [], 'function');
        this.updateObjectList('aliasesList', [], 'alias');
        
        // Clear messages
        this.clearMessages();
        
        // Reset textarea height
        const textarea = document.getElementById('sourceCode');
        textarea.style.height = 'auto';
    }

    async copyOutput() {
        const daxOutput = document.getElementById('daxOutput');
        const codeElement = daxOutput.querySelector('code');
        
        if (codeElement && codeElement.textContent) {
            try {
                await navigator.clipboard.writeText(codeElement.textContent);
                
                // Visual feedback
                const copyBtn = document.getElementById('copyBtn');
                const originalText = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i data-feather="check" class="me-1"></i>Copied!';
                feather.replace();
                
                setTimeout(() => {
                    copyBtn.innerHTML = originalText;
                    feather.replace();
                }, 2000);
                
            } catch (error) {
                console.error('Failed to copy to clipboard:', error);
                this.showError('Failed to copy to clipboard. Please copy manually.');
            }
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const app = new ConverterApp();
    
    // Re-initialize Feather icons after dynamic content updates
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Check if any of the added nodes contain feather icons
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        const featherIcons = node.querySelectorAll('[data-feather]');
                        if (featherIcons.length > 0 || node.hasAttribute('data-feather')) {
                            feather.replace();
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
