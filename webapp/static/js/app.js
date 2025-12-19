// Codemeta Generator Web Application
// Main JavaScript logic for handling UI interactions and API calls

let currentCodemetaData = null;

// DOM Elements
const githubUrlInput = document.getElementById('github-url');
const generateBtn = document.getElementById('generate-btn');
const errorMessage = document.getElementById('error-message');
const tabsContainer = document.getElementById('tabs-container');
const terminalOutput = document.getElementById('terminal-output');
const jsonOutput = document.getElementById('json-output');
const editForm = document.getElementById('edit-form');

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
}

// Generate button click handler
generateBtn.addEventListener('click', async () => {
    const githubUrl = githubUrlInput.value.trim();
    
    if (!githubUrl) {
        showError('Please enter a GitHub repository URL');
        return;
    }
    
    // Validate URL format
    if (!isValidGitHubUrl(githubUrl)) {
        showError('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)');
        return;
    }
    
    hideError();
    startGeneration();
    
    try {
        await generateCodemeta(githubUrl);
    } catch (error) {
        showError(`Error: ${error.message}`);
        stopGeneration();
    }
});

function isValidGitHubUrl(url) {
    try {
        const parsed = new URL(url);
        return parsed.hostname === 'github.com' || parsed.hostname === 'www.github.com';
    } catch {
        return false;
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function startGeneration() {
    generateBtn.disabled = true;
    generateBtn.querySelector('.btn-text').style.display = 'none';
    generateBtn.querySelector('.btn-spinner').style.display = 'inline-block';
    
    // Show tabs container and switch to terminal
    tabsContainer.style.display = 'block';
    switchTab('terminal');
    
    // Clear previous output
    terminalOutput.innerHTML = '';
    jsonOutput.textContent = '';
    editForm.innerHTML = '';
}

function stopGeneration() {
    generateBtn.disabled = false;
    generateBtn.querySelector('.btn-text').style.display = 'inline';
    generateBtn.querySelector('.btn-spinner').style.display = 'none';
}

async function generateCodemeta(githubUrl) {
    return new Promise((resolve, reject) => {
        // Use fetch with streaming
        fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ github_url: githubUrl })
        })
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            function readStream() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        stopGeneration();
                        resolve();
                        return;
                    }
                    
                    // Decode the chunk
                    const chunk = decoder.decode(value, { stream: true });
                    
                    // Process SSE events
                    const events = chunk.split('\n\n').filter(e => e.trim());
                    events.forEach(event => {
                        if (event.startsWith('data: ')) {
                            const data = JSON.parse(event.substring(6));
                            handleStreamEvent(data);
                        }
                    });
                    
                    // Continue reading
                    readStream();
                });
            }
            
            readStream();
        })
        .catch(error => {
            stopGeneration();
            reject(error);
        });
    });
}

function handleStreamEvent(data) {
    const { type, message, codemeta } = data;
    
    switch (type) {
        case 'start':
            addTerminalLine(message, 'info');
            break;
        
        case 'output':
            addTerminalLine(message);
            break;
        
        case 'complete':
            addTerminalLine('✅ Generation completed successfully!', 'success');
            currentCodemetaData = codemeta;
            displayJsonResult(codemeta);
            buildEditForm(codemeta);
            break;
        
        case 'error':
            addTerminalLine(`❌ Error: ${message}`, 'error');
            showError(message);
            break;
    }
}

function addTerminalLine(text, className = '') {
    const line = document.createElement('div');
    line.className = `terminal-line ${className}`;
    line.textContent = text;
    terminalOutput.appendChild(line);
    
    // Auto-scroll to bottom
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function displayJsonResult(codemeta) {
    jsonOutput.textContent = JSON.stringify(codemeta, null, 2);
}

function buildEditForm(codemeta) {
    editForm.innerHTML = '';
    
    // Recursively build form fields for all properties
    buildFormFields(codemeta, editForm, '');
}

function buildFormFields(obj, container, prefix) {
    // Sort keys to show them in a consistent order
    const keys = Object.keys(obj).sort();
    
    keys.forEach(key => {
        const value = obj[key];
        const fieldPath = prefix ? `${prefix}.${key}` : key;
        
        if (value === null || value === undefined) {
            // Skip null/undefined values
            return;
        }
        
        if (Array.isArray(value)) {
            // Handle arrays
            buildArrayField(key, value, container, fieldPath);
        } else if (typeof value === 'object') {
            // Handle nested objects
            buildNestedObjectField(key, value, container, fieldPath);
        } else {
            // Handle primitive values (string, number, boolean)
            buildPrimitiveField(key, value, container, fieldPath);
        }
    });
}

function buildPrimitiveField(key, value, container, fieldPath) {
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group';
    
    const label = document.createElement('label');
    label.textContent = formatLabel(key);
    label.htmlFor = `edit-${fieldPath}`;
    
    let input;
    if (typeof value === 'string' && value.length > 100) {
        input = document.createElement('textarea');
        input.rows = 3;
    } else {
        input = document.createElement('input');
        input.type = typeof value === 'number' ? 'number' : 'text';
    }
    
    input.id = `edit-${fieldPath}`;
    input.name = fieldPath;
    input.value = value;
    
    formGroup.appendChild(label);
    formGroup.appendChild(input);
    container.appendChild(formGroup);
}

function buildArrayField(key, array, container, fieldPath) {
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group array-field';
    
    const label = document.createElement('label');
    label.textContent = formatLabel(key);
    
    const arrayContainer = document.createElement('div');
    arrayContainer.className = 'array-container';
    
    // Check if array contains objects or primitives
    if (array.length > 0 && typeof array[0] === 'object' && array[0] !== null) {
        // Array of objects - create nested fields for each
        array.forEach((item, index) => {
            const itemContainer = document.createElement('div');
            itemContainer.className = 'nested-object';
            
            const itemHeader = document.createElement('div');
            itemHeader.className = 'nested-header';
            itemHeader.textContent = `${formatLabel(key)} #${index + 1}`;
            itemContainer.appendChild(itemHeader);
            
            buildFormFields(item, itemContainer, `${fieldPath}[${index}]`);
            arrayContainer.appendChild(itemContainer);
        });
    } else {
        // Array of primitives - create a textarea with comma-separated values
        const textarea = document.createElement('textarea');
        textarea.id = `edit-${fieldPath}`;
        textarea.name = fieldPath;
        textarea.rows = 2;
        textarea.value = array.join(', ');
        textarea.placeholder = 'Comma-separated values';
        arrayContainer.appendChild(textarea);
    }
    
    formGroup.appendChild(label);
    formGroup.appendChild(arrayContainer);
    container.appendChild(formGroup);
}

function buildNestedObjectField(key, obj, container, fieldPath) {
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group nested-field';
    
    const nestedContainer = document.createElement('div');
    nestedContainer.className = 'nested-object';
    
    const nestedHeader = document.createElement('div');
    nestedHeader.className = 'nested-header';
    nestedHeader.textContent = formatLabel(key);
    nestedContainer.appendChild(nestedHeader);
    
    // Recursively build fields for nested object
    buildFormFields(obj, nestedContainer, fieldPath);
    
    formGroup.appendChild(nestedContainer);
    container.appendChild(formGroup);
}

function formatLabel(key) {
    // Convert camelCase or snake_case to readable label
    return key
        .replace(/([A-Z])/g, ' $1')
        .replace(/_/g, ' ')
        .replace(/^./, str => str.toUpperCase())
        .trim();
}

function collectFormData() {
    // Collect all form inputs and reconstruct the codemeta object
    const formData = new FormData(editForm);
    const result = {};
    
    formData.forEach((value, key) => {
        setNestedValue(result, key, value);
    });
    
    return result;
}

function setNestedValue(obj, path, value) {
    const parts = path.split('.');
    let current = obj;
    
    for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i];
        
        // Handle array indices
        const arrayMatch = part.match(/^(.+)\[(\d+)\]$/);
        if (arrayMatch) {
            const arrayKey = arrayMatch[1];
            const index = parseInt(arrayMatch[2]);
            
            if (!current[arrayKey]) {
                current[arrayKey] = [];
            }
            if (!current[arrayKey][index]) {
                current[arrayKey][index] = {};
            }
            current = current[arrayKey][index];
        } else {
            if (!current[part]) {
                current[part] = {};
            }
            current = current[part];
        }
    }
    
    const lastPart = parts[parts.length - 1];
    const arrayMatch = lastPart.match(/^(.+)\[(\d+)\]$/);
    
    if (arrayMatch) {
        const arrayKey = arrayMatch[1];
        const index = parseInt(arrayMatch[2]);
        
        if (!current[arrayKey]) {
            current[arrayKey] = [];
        }
        current[arrayKey][index] = value;
    } else {
        // Check if value looks like a comma-separated list
        if (typeof value === 'string' && value.includes(',')) {
            current[lastPart] = value.split(',').map(v => v.trim()).filter(v => v);
        } else {
            current[lastPart] = value;
        }
    }
}

// Clear terminal button
document.getElementById('clear-terminal').addEventListener('click', () => {
    terminalOutput.innerHTML = '';
});

// Copy JSON button
document.getElementById('copy-json').addEventListener('click', () => {
    const jsonText = jsonOutput.textContent;
    navigator.clipboard.writeText(jsonText).then(() => {
        alert('JSON copied to clipboard!');
    });
});

// Download JSON button
document.getElementById('download-json').addEventListener('click', () => {
    if (!currentCodemetaData) return;
    
    const jsonText = JSON.stringify(currentCodemetaData, null, 2);
    const blob = new Blob([jsonText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'codemeta.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// Save edits button
document.getElementById('save-edits').addEventListener('click', () => {
    if (!currentCodemetaData) return;
    
    // Collect form data and reconstruct the object
    const updatedCodemeta = collectFormData();
    
    // Update current data and JSON display
    currentCodemetaData = updatedCodemeta;
    displayJsonResult(updatedCodemeta);
    
    alert('Changes saved! You can now download the updated JSON.');
    switchTab('json');
});

// Allow Enter key to trigger generation
githubUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        generateBtn.click();
    }
});
