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
        // Create EventSource for Server-Sent Events
        const eventSource = new EventSource(`/api/generate?github_url=${encodeURIComponent(githubUrl)}`);
        
        // This is a workaround for POST with EventSource
        // We'll use fetch with POST instead
        eventSource.close();
        
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
    
    // Create form fields for common metadata properties
    const fields = [
        { key: 'name', label: 'Name', type: 'text' },
        { key: 'description', label: 'Description', type: 'textarea' },
        { key: 'version', label: 'Version', type: 'text' },
        { key: 'license', label: 'License', type: 'text' },
        { key: 'author', label: 'Author', type: 'text' },
        { key: 'codeRepository', label: 'Code Repository', type: 'text' },
        { key: 'applicationCategory', label: 'Application Category', type: 'text' },
        { key: 'programmingLanguage', label: 'Programming Language', type: 'text' },
        { key: 'keywords', label: 'Keywords (comma-separated)', type: 'textarea' },
    ];
    
    fields.forEach(field => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';
        
        const label = document.createElement('label');
        label.textContent = field.label;
        label.htmlFor = `edit-${field.key}`;
        
        let input;
        if (field.type === 'textarea') {
            input = document.createElement('textarea');
        } else {
            input = document.createElement('input');
            input.type = field.type;
        }
        
        input.id = `edit-${field.key}`;
        input.name = field.key;
        
        // Set value from codemeta
        const value = getNestedValue(codemeta, field.key);
        if (value !== undefined && value !== null) {
            if (Array.isArray(value)) {
                input.value = value.map(v => typeof v === 'object' ? v.name || JSON.stringify(v) : v).join(', ');
            } else if (typeof value === 'object') {
                input.value = value.name || JSON.stringify(value);
            } else {
                input.value = value;
            }
        }
        
        formGroup.appendChild(label);
        formGroup.appendChild(input);
        editForm.appendChild(formGroup);
    });
}

function getNestedValue(obj, key) {
    return obj[key];
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
    
    // Collect form data
    const formData = new FormData(editForm);
    const updatedCodemeta = { ...currentCodemetaData };
    
    formData.forEach((value, key) => {
        if (key === 'keywords' || key === 'programmingLanguage') {
            // Split comma-separated values
            updatedCodemeta[key] = value.split(',').map(v => v.trim()).filter(v => v);
        } else {
            updatedCodemeta[key] = value;
        }
    });
    
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
