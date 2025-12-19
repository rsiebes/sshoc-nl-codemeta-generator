// Codemeta Generator Web Application
// Main JavaScript logic for handling UI interactions and API calls

let currentCodemetaData = null;
let undoStack = [];

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
    undoStack = [];
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
    formGroup.dataset.fieldPath = fieldPath;
    
    const label = document.createElement('label');
    label.textContent = formatLabel(key);
    
    const arrayContainer = document.createElement('div');
    arrayContainer.className = 'array-container';
    
    // Check if array contains objects or primitives
    if (array.length > 0 && typeof array[0] === 'object' && array[0] !== null) {
        // Add undo button container at the top of the array section
        const undoContainer = document.createElement('div');
        undoContainer.className = 'undo-container';
        undoContainer.style.display = 'none';
        undoContainer.dataset.arrayPath = fieldPath;
        
        const undoBtn = document.createElement('button');
        undoBtn.type = 'button';
        undoBtn.className = 'btn-undo-persistent';
        undoBtn.innerHTML = '↶ Undo last removal';
        undoBtn.onclick = () => undoForArray(fieldPath);
        
        undoContainer.appendChild(undoBtn);
        arrayContainer.appendChild(undoContainer);
        
        // Add "Add" button container
        const addContainer = document.createElement('div');
        addContainer.className = 'add-container';
        
        const addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.className = 'btn-add';
        addBtn.innerHTML = '+ Add ' + singularize(formatLabel(key));
        addBtn.onclick = () => addArrayItem(arrayContainer, fieldPath, key, array[0]);
        
        addContainer.appendChild(addBtn);
        
        // Add Wikidata lookup button for keywords
        if (key.toLowerCase().includes('keyword')) {
            const wikidataBtn = document.createElement('button');
            wikidataBtn.type = 'button';
            wikidataBtn.className = 'btn-wikidata';
            wikidataBtn.innerHTML = '🔍 Add Keyword via Wikidata';
            wikidataBtn.onclick = () => openWikidataSearch(arrayContainer, fieldPath, key, array[0]);
            addContainer.appendChild(wikidataBtn);
        }
        
        arrayContainer.appendChild(addContainer);
        
        // Array of objects - create nested fields for each
        array.forEach((item, index) => {
            const itemContainer = document.createElement('div');
            itemContainer.className = 'nested-object array-item';
            itemContainer.dataset.arrayPath = fieldPath;
            itemContainer.dataset.arrayIndex = index;
            
            const itemHeader = document.createElement('div');
            itemHeader.className = 'nested-header';
            
            const headerText = document.createElement('span');
            headerText.textContent = `${formatLabel(key)} #${index + 1}`;
            itemHeader.appendChild(headerText);
            
            // Add remove button
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'btn-remove';
            removeBtn.textContent = '🗑️ Remove';
            removeBtn.onclick = () => removeArrayItem(itemContainer, fieldPath, index);
            itemHeader.appendChild(removeBtn);
            
            itemContainer.appendChild(itemHeader);
            buildFormFields(item, itemContainer, `${fieldPath}[${index}]`);
            
            // Add ORCID lookup button if this is a contributor/author field
            if (key.toLowerCase().includes('contributor') || key.toLowerCase().includes('author')) {
                addOrcidLookupButton(itemContainer, fieldPath, index);
            }
            
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

function singularize(word) {
    // Convert plural words to singular
    // Handle common English pluralization rules
    
    if (word.endsWith('ies')) {
        // categories -> category, properties -> property
        return word.slice(0, -3) + 'y';
    } else if (word.endsWith('sses') || word.endsWith('xes') || word.endsWith('ches') || word.endsWith('shes')) {
        // classes -> class, boxes -> box, branches -> branch, dishes -> dish
        return word.slice(0, -2);
    } else if (word.endsWith('s') && !word.endsWith('ss')) {
        // contributors -> contributor, authors -> author, keywords -> keyword
        // but not: class -> clas
        return word.slice(0, -1);
    }
    
    // Already singular or unknown pattern
    return word;
}

function addArrayItem(arrayContainer, arrayPath, arrayKey, templateItem) {
    // Get the current number of items in this array
    const existingItems = arrayContainer.querySelectorAll('.array-item');
    const newIndex = existingItems.length;
    
    // Create a new item container
    const itemContainer = document.createElement('div');
    itemContainer.className = 'nested-object array-item';
    itemContainer.dataset.arrayPath = arrayPath;
    itemContainer.dataset.arrayIndex = newIndex;
    
    const itemHeader = document.createElement('div');
    itemHeader.className = 'nested-header';
    
    const headerText = document.createElement('span');
    headerText.textContent = `${formatLabel(arrayKey)} #${newIndex + 1}`;
    itemHeader.appendChild(headerText);
    
    // Add remove button
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn-remove';
    removeBtn.textContent = '🗑️ Remove';
    removeBtn.onclick = () => removeArrayItem(itemContainer, arrayPath, newIndex);
    itemHeader.appendChild(removeBtn);
    
    itemContainer.appendChild(itemHeader);
    
    // Create empty fields based on the template item structure
    const emptyItem = createEmptyItem(templateItem);
    buildFormFields(emptyItem, itemContainer, `${arrayPath}[${newIndex}]`);
    
    // Add ORCID lookup button if this is a contributor/author field
    if (arrayKey.toLowerCase().includes('contributor') || arrayKey.toLowerCase().includes('author')) {
        addOrcidLookupButton(itemContainer, arrayPath, newIndex);
    }
    
    // Append to array container
    arrayContainer.appendChild(itemContainer);
    
    // Scroll to the new item
    itemContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function createEmptyItem(templateItem) {
    // Create an empty object with the same structure as the template
    const emptyItem = {};
    
    for (const key in templateItem) {
        const value = templateItem[key];
        
        if (Array.isArray(value)) {
            emptyItem[key] = [];
        } else if (typeof value === 'object' && value !== null) {
            emptyItem[key] = createEmptyItem(value);
        } else if (typeof value === 'number') {
            emptyItem[key] = 0;
        } else {
            emptyItem[key] = '';
        }
    }
    
    return emptyItem;
}

function addOrcidLookupButton(itemContainer, arrayPath, index) {
    // Find the @id field (ORCID URL)
    const idInput = itemContainer.querySelector(`input[name="${arrayPath}[${index}].@id"]`);
    
    if (!idInput) return;
    
    // Create lookup button container
    const lookupContainer = document.createElement('div');
    lookupContainer.className = 'orcid-lookup-container';
    lookupContainer.style.marginTop = '0.5rem';
    
    const lookupBtn = document.createElement('button');
    lookupBtn.type = 'button';
    lookupBtn.className = 'btn-orcid-lookup';
    lookupBtn.innerHTML = '🔍 Auto-fill from ORCID';
    lookupBtn.onclick = () => lookupOrcidData(itemContainer, arrayPath, index, idInput.value);
    
    const statusSpan = document.createElement('span');
    statusSpan.className = 'orcid-status';
    statusSpan.style.marginLeft = '1rem';
    
    lookupContainer.appendChild(lookupBtn);
    lookupContainer.appendChild(statusSpan);
    
    // Insert after the @id field's form group
    const idFormGroup = idInput.closest('.form-group');
    if (idFormGroup && idFormGroup.nextSibling) {
        idFormGroup.parentNode.insertBefore(lookupContainer, idFormGroup.nextSibling);
    } else if (idFormGroup) {
        idFormGroup.parentNode.appendChild(lookupContainer);
    }
}

async function lookupOrcidData(itemContainer, arrayPath, index, orcidUrl) {
    const statusSpan = itemContainer.querySelector('.orcid-status');
    
    if (!orcidUrl || !orcidUrl.includes('orcid.org')) {
        statusSpan.textContent = '⚠️ Please enter a valid ORCID URL';
        statusSpan.style.color = '#ef4444';
        return;
    }
    
    // Extract ORCID ID from URL
    const orcidMatch = orcidUrl.match(/\d{4}-\d{4}-\d{4}-\d{3}[0-9X]/);
    if (!orcidMatch) {
        statusSpan.textContent = '⚠️ Invalid ORCID format';
        statusSpan.style.color = '#ef4444';
        return;
    }
    
    const orcidId = orcidMatch[0];
    statusSpan.textContent = '⏳ Looking up ORCID data...';
    statusSpan.style.color = '#64748b';
    
    try {
        // Call ORCID public API for person data (name, email)
        const personResponse = await fetch(`https://pub.orcid.org/v3.0/${orcidId}/person`, {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!personResponse.ok) {
            throw new Error('ORCID lookup failed');
        }
        
        const personData = await personResponse.json();
        console.log('ORCID person data:', personData);
        
        // Extract name
        if (personData.name) {
            const givenNames = personData.name['given-names']?.value || '';
            const familyName = personData.name['family-name']?.value || '';
            const fullName = `${givenNames} ${familyName}`.trim();
            
            const nameInput = itemContainer.querySelector(`input[name="${arrayPath}[${index}].name"]`);
            if (nameInput && fullName) {
                nameInput.value = fullName;
                console.log('Set name:', fullName);
            }
        }
        
        // Extract email (if public)
        if (personData.emails && personData.emails.email && personData.emails.email.length > 0) {
            const emailData = personData.emails.email[0];
            const email = emailData.email || emailData.value;
            const emailInput = itemContainer.querySelector(`input[name="${arrayPath}[${index}].email"]`);
            if (emailInput && email) {
                emailInput.value = email;
                console.log('Set email:', email);
            }
        }
        
        // Fetch employments separately
        try {
            const employmentsResponse = await fetch(`https://pub.orcid.org/v3.0/${orcidId}/employments`, {
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (employmentsResponse.ok) {
                const employmentsData = await employmentsResponse.json();
                console.log('ORCID employments data:', employmentsData);
                
                // Extract most recent employment
                const affiliationGroups = employmentsData['affiliation-group'] || [];
                if (affiliationGroups.length > 0) {
                    const firstGroup = affiliationGroups[0];
                    const summaries = firstGroup.summaries || [];
                    if (summaries.length > 0) {
                        const employmentSummary = summaries[0]['employment-summary'];
                        const affiliationName = employmentSummary?.organization?.name || '';
                        
                        if (affiliationName) {
                            // Try to find affiliation name field
                            const affiliationInput = itemContainer.querySelector(`input[name="${arrayPath}[${index}].affiliation.name"]`);
                            if (affiliationInput) {
                                affiliationInput.value = affiliationName;
                                console.log('Set affiliation:', affiliationName);
                            }
                        }
                    }
                }
            }
        } catch (empError) {
            console.log('Could not fetch employments:', empError);
            // Continue even if employments fail
        }
        
        statusSpan.textContent = '✅ Data loaded from ORCID';
        statusSpan.style.color = '#10b981';
        
        // Clear status after 3 seconds
        setTimeout(() => {
            statusSpan.textContent = '';
        }, 3000);
        
    } catch (error) {
        console.error('ORCID lookup error:', error);
        statusSpan.textContent = '❌ Failed to fetch ORCID data';
        statusSpan.style.color = '#ef4444';
    }
}

function removeArrayItem(itemContainer, arrayPath, index) {
    // Save current state to undo stack for this specific array
    saveToUndoStack(arrayPath);
    
    // Remove the item from the DOM with animation
    itemContainer.style.opacity = '0.5';
    itemContainer.style.transition = 'opacity 0.3s';
    
    setTimeout(() => {
        itemContainer.remove();
        
        // Update the data and rebuild JSON
        updateCurrentDataAndJson();
        
        // Show undo button for this array
        showUndoButton(arrayPath);
    }, 300);
}

function saveToUndoStack(arrayPath) {
    // Save a deep copy of the current state with the array path
    const undoEntry = {
        arrayPath: arrayPath,
        state: JSON.parse(JSON.stringify(currentCodemetaData))
    };
    
    undoStack.push(undoEntry);
    
    // Limit undo stack to 10 items
    if (undoStack.length > 10) {
        undoStack.shift();
    }
}

function undoForArray(arrayPath) {
    // Find the most recent undo entry for this array path
    let undoIndex = -1;
    for (let i = undoStack.length - 1; i >= 0; i--) {
        if (undoStack[i].arrayPath === arrayPath) {
            undoIndex = i;
            break;
        }
    }
    
    if (undoIndex === -1) {
        alert('Nothing to undo for this section');
        return;
    }
    
    // Restore previous state
    const undoEntry = undoStack[undoIndex];
    currentCodemetaData = undoEntry.state;
    
    // Remove this entry from undo stack
    undoStack.splice(undoIndex, 1);
    
    // Rebuild the form and JSON display
    buildEditForm(currentCodemetaData);
    displayJsonResult(currentCodemetaData);
    
    // Check if there are more undo entries for this array
    const hasMoreUndos = undoStack.some(entry => entry.arrayPath === arrayPath);
    if (!hasMoreUndos) {
        hideUndoButton(arrayPath);
    }
}

function showUndoButton(arrayPath) {
    // Find the undo container for this array path
    const undoContainer = document.querySelector(`.undo-container[data-array-path="${arrayPath}"]`);
    if (undoContainer) {
        undoContainer.style.display = 'block';
    }
}

function hideUndoButton(arrayPath) {
    // Find the undo container for this array path
    const undoContainer = document.querySelector(`.undo-container[data-array-path="${arrayPath}"]`);
    if (undoContainer) {
        undoContainer.style.display = 'none';
    }
}

function updateCurrentDataAndJson() {
    // Collect form data and update current codemeta
    currentCodemetaData = collectFormData();
    displayJsonResult(currentCodemetaData);
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
    
    // Clear undo stack since we're saving
    undoStack = [];
    
    // Hide all undo buttons
    document.querySelectorAll('.undo-container').forEach(container => {
        container.style.display = 'none';
    });
    
    alert('Changes saved! You can now download the updated JSON.');
    switchTab('json');
});

// Allow Enter key to trigger generation
githubUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        generateBtn.click();
    }
});

// Wikidata Search Functionality
function openWikidataSearch(arrayContainer, arrayPath, arrayKey, templateItem) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'wikidata-modal';
    modal.innerHTML = `
        <div class="wikidata-modal-content">
            <div class="wikidata-modal-header">
                <h3>Search Wikidata for Keywords</h3>
                <button class="wikidata-close" onclick="closeWikidataModal()">&times;</button>
            </div>
            <div class="wikidata-modal-body">
                <input type="text" id="wikidata-search-input" placeholder="Type to search Wikidata..." />
                <div id="wikidata-results" class="wikidata-results"></div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Store context for later use
    modal.dataset.arrayContainer = arrayContainer;
    modal.dataset.arrayPath = arrayPath;
    modal.dataset.arrayKey = arrayKey;
    modal.dataset.templateItem = JSON.stringify(templateItem);
    
    // Focus on search input
    const searchInput = document.getElementById('wikidata-search-input');
    searchInput.focus();
    
    // Add search event listener with debounce
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            document.getElementById('wikidata-results').innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            searchWikidata(query);
        }, 300);
    });
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeWikidataModal();
        }
    });
}

function closeWikidataModal() {
    const modal = document.querySelector('.wikidata-modal');
    if (modal) {
        modal.remove();
    }
}

window.closeWikidataModal = closeWikidataModal;

async function checkPhraseConfidence(phrase) {
    try {
        // Search for the exact phrase
        const response = await fetch(
            `https://www.wikidata.org/w/api.php?` +
            `action=wbsearchentities&` +
            `search=${encodeURIComponent(phrase)}&` +
            `language=en&` +
            `limit=3&` +
            `format=json&` +
            `origin=*`
        );
        
        if (!response.ok) {
            return { isHighConfidence: false, reason: 'API error' };
        }
        
        const data = await response.json();
        const results = data.search || [];
        
        if (results.length === 0) {
            return { isHighConfidence: false, reason: 'No results' };
        }
        
        const topResult = results[0];
        const label = (topResult.label || '').toLowerCase();
        const description = (topResult.description || '').toLowerCase();
        const phraseNormalized = phrase.toLowerCase();
        
        // Calculate confidence score
        let confidence = 0;
        
        // Exact label match is very strong indicator
        if (label === phraseNormalized) {
            confidence += 50;
        } else if (label.includes(phraseNormalized) || phraseNormalized.includes(label)) {
            confidence += 30;
        }
        
        // Has a meaningful description
        if (description && description.length > 20) {
            confidence += 20;
        }
        
        // Check for well-known software/tech terms
        const knownPhrases = [
            'creative commons', 'machine learning', 'deep learning', 'web scraping',
            'web crawler', 'natural language', 'artificial intelligence', 'neural network',
            'open source', 'version control', 'data science', 'computer vision',
            'software engineering', 'web development', 'mobile development',
            'cloud computing', 'distributed systems', 'operating system'
        ];
        
        if (knownPhrases.includes(phraseNormalized)) {
            confidence += 30;
        }
        
        // Check if description contains software-related terms
        const softwareTerms = [
            'software', 'programming', 'computer', 'technology', 'license',
            'organization', 'framework', 'library', 'language', 'tool',
            'application', 'system', 'protocol', 'algorithm', 'method'
        ];
        
        for (const term of softwareTerms) {
            if (description.includes(term)) {
                confidence += 10;
                break; // Only count once
            }
        }
        
        // High confidence threshold
        const isHighConfidence = confidence >= 60;
        
        console.log(`Phrase confidence for "${phrase}": ${confidence} (${isHighConfidence ? 'HIGH' : 'LOW'})`);
        console.log(`  Top result: ${topResult.label} - ${topResult.description}`);
        
        return {
            isHighConfidence,
            confidence,
            topResult,
            reason: isHighConfidence ? 'Strong match found' : 'Weak or ambiguous match'
        };
        
    } catch (error) {
        console.error('Error checking phrase confidence:', error);
        return { isHighConfidence: false, reason: 'Error' };
    }
}

function scoreAndSortResults(results, query) {
    // Software-related keywords to boost relevance
    const softwareKeywords = [
        'software', 'programming', 'language', 'library', 'framework', 'tool',
        'application', 'code', 'computer', 'algorithm', 'data', 'web',
        'api', 'database', 'system', 'technology', 'development', 'computing',
        'digital', 'internet', 'network', 'protocol', 'format', 'standard',
        'method', 'technique', 'process', 'function', 'module', 'package',
        'platform', 'service', 'interface', 'architecture', 'design pattern',
        'machine learning', 'artificial intelligence', 'neural network',
        'open source', 'repository', 'version control', 'git'
    ];
    
    // Keywords to penalize (non-software contexts)
    const penaltyKeywords = [
        'person', 'human', 'family name', 'given name', 'surname',
        'town', 'city', 'place', 'location', 'country', 'region',
        'song', 'album', 'music', 'band', 'artist', 'film', 'movie',
        'book', 'novel', 'author', 'writer', 'painting', 'artwork',
        'sport', 'game', 'player', 'team', 'athlete', 'swimming',
        'physical', 'biological', 'medical', 'anatomical', 'disease'
    ];
    
    results.forEach(result => {
        let score = 0;
        const description = (result.description || '').toLowerCase();
        const label = (result.label || '').toLowerCase();
        const combined = `${label} ${description}`;
        
        // Boost score for software-related terms
        for (const keyword of softwareKeywords) {
            if (combined.includes(keyword)) {
                score += 20;
            }
        }
        
        // Penalize non-software contexts
        for (const keyword of penaltyKeywords) {
            if (combined.includes(keyword)) {
                score -= 30;
            }
        }
        
        // Boost if label closely matches query
        if (label === query.toLowerCase()) {
            score += 15;
        } else if (label.includes(query.toLowerCase())) {
            score += 10;
        }
        
        // Boost if description exists (more informative)
        if (description && description.length > 10) {
            score += 5;
        }
        
        result.relevanceScore = Math.max(0, score);
    });
    
    // Sort by relevance score (descending)
    return results.sort((a, b) => b.relevanceScore - a.relevanceScore);
}

async function searchWikidata(query) {
    const resultsDiv = document.getElementById('wikidata-results');
    resultsDiv.innerHTML = '<div class="wikidata-loading">⏳ Searching Wikidata...</div>';
    
    try {
        // Check if query is a multi-word phrase
        const isPhrase = query.trim().split(/\s+/).length > 1;
        
        let searches = [];
        
        if (isPhrase) {
            // For phrases, first check if the exact phrase has a strong match
            const phraseConfidence = await checkPhraseConfidence(query);
            
            if (phraseConfidence.isHighConfidence) {
                // High confidence phrase match - only search the full phrase
                searches = [
                    query,
                    `${query} software`,
                    `${query} programming`
                ];
                console.log(`High confidence phrase detected: "${query}" - skipping individual words`);
            } else {
                // Low confidence - include individual word searches
                searches = [
                    query,
                    `${query} software`,
                    `${query} programming`
                ];
                console.log(`Low confidence phrase: "${query}" - using standard search`);
            }
        } else {
            // Single word - use standard multi-context search
            searches = [
                query,
                `${query} software`,
                `${query} programming`
            ];
        }
        
        // Collect all results from multiple searches
        const allResults = [];
        const seenIds = new Set();
        
        for (const searchQuery of searches) {
            const response = await fetch(
                `https://www.wikidata.org/w/api.php?` +
                `action=wbsearchentities&` +
                `search=${encodeURIComponent(searchQuery)}&` +
                `language=en&` +
                `limit=10&` +
                `format=json&` +
                `origin=*`
            );
            
            if (response.ok) {
                const data = await response.json();
                const searchResults = data.search || [];
                
                // Add unique results
                for (const result of searchResults) {
                    if (!seenIds.has(result.id)) {
                        seenIds.add(result.id);
                        allResults.push(result);
                    }
                }
            }
        }
        
        // Score and sort results based on software relevance
        const results = scoreAndSortResults(allResults, query);
        
        if (results.length === 0) {
            resultsDiv.innerHTML = '<div class="wikidata-no-results">No results found</div>';
            return;
        }
        
        // Display results (limit to top 10)
        resultsDiv.innerHTML = '';
        results.slice(0, 10).forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'wikidata-result-item';
            
            // Add relevance badge if highly relevant
            const relevanceBadge = result.relevanceScore > 50 ? 
                '<span class="wikidata-relevance-badge">🎯 Software-related</span>' : '';
            
            resultItem.innerHTML = `
                <div class="wikidata-result-title">${result.label} ${relevanceBadge}</div>
                <div class="wikidata-result-description">${result.description || 'No description'}</div>
                <div class="wikidata-result-id">${result.id}</div>
            `;
            
            resultItem.onclick = () => selectWikidataResult(result);
            resultsDiv.appendChild(resultItem);
        });
        
    } catch (error) {
        console.error('Wikidata search error:', error);
        resultsDiv.innerHTML = '<div class="wikidata-error">❌ Error searching Wikidata</div>';
    }
}

function selectWikidataResult(result) {
    const modal = document.querySelector('.wikidata-modal');
    if (!modal) return;
    
    // Get stored context
    const arrayPath = modal.dataset.arrayPath;
    const arrayKey = modal.dataset.arrayKey;
    const templateItem = JSON.parse(modal.dataset.templateItem);
    
    // Find the array container (need to search in the DOM)
    const arrayContainers = document.querySelectorAll('.array-container');
    let targetContainer = null;
    
    for (const container of arrayContainers) {
        const parent = container.closest('.array-field');
        if (parent && parent.dataset.fieldPath === arrayPath) {
            targetContainer = container;
            break;
        }
    }
    
    if (!targetContainer) {
        console.error('Could not find array container');
        closeWikidataModal();
        return;
    }
    
    // Create new keyword item
    const existingItems = targetContainer.querySelectorAll('.array-item');
    const newIndex = existingItems.length;
    
    const itemContainer = document.createElement('div');
    itemContainer.className = 'nested-object array-item';
    itemContainer.dataset.arrayPath = arrayPath;
    itemContainer.dataset.arrayIndex = newIndex;
    
    const itemHeader = document.createElement('div');
    itemHeader.className = 'nested-header';
    
    const headerText = document.createElement('span');
    headerText.textContent = `${formatLabel(arrayKey)} #${newIndex + 1}`;
    itemHeader.appendChild(headerText);
    
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn-remove';
    removeBtn.textContent = '🗑️ Remove';
    removeBtn.onclick = () => removeArrayItem(itemContainer, arrayPath, newIndex);
    itemHeader.appendChild(removeBtn);
    
    itemContainer.appendChild(itemHeader);
    
    // Create fields with Wikidata data
    const keywordData = {
        '@type': 'DefinedTerm',
        '@id': `http://www.wikidata.org/entity/${result.id}`,
        'name': result.label,
        'description': result.description || ''
    };
    
    buildFormFields(keywordData, itemContainer, `${arrayPath}[${newIndex}]`);
    
    // Append to container
    targetContainer.appendChild(itemContainer);
    
    // Scroll to new item
    itemContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Close modal
    closeWikidataModal();
}
