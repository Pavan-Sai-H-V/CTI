// Menu toggle function
function toggleMenu() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
}

// Clear screen function
function clearScreen() {
    const threatInput = document.getElementById('threatInput');
    const threatList = document.getElementById('threatList');
    threatInput.value = '';
    threatList.innerHTML = '';
}

async function submitThreat() {
    const threatInput = document.getElementById('threatInput');
    const threatText = threatInput.value.trim();
    
    if (!threatText) {
        alert('Please enter a threat description');
        return;
    }

    try {
        const response = await fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ threat: threatText })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        
        // Format confidence scores for display
        const confidenceHtml = data.confidence_scores
            .map(([category, score]) => `${category}: ${(score * 100).toFixed(1)}%`)
            .join('<br>');
            
        alert(`Threat submitted successfully!\n\nCategory: ${data.category}\n\nConfidence Scores:\n${data.confidence_scores.map(([cat, score]) => `${cat}: ${(score * 100).toFixed(1)}%`).join('\n')}`);
        
        threatInput.value = ''; // Clear the input
        loadThreats(); // Refresh the threats list
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to submit threat. Please try again.');
    }
}

async function loadThreats() {
    try {
        const response = await fetch('/threats');
        const threats = await response.json();
        const threatList = document.getElementById('threatList');
        threatList.innerHTML = ''; // Clear existing list

        if (threats.length === 0) {
            threatList.innerHTML = '<li class="no-threats">No threats submitted yet.</li>';
            return;
        }

        threats.forEach(threat => {
            const li = document.createElement('li');
            li.className = 'threat-item';
            
            // Format confidence scores if they exist
            const confidenceHtml = threat.confidence_scores
                ? threat.confidence_scores
                    .map(([category, score]) => `<small class="confidence-score">${category}: ${(score * 100).toFixed(1)}%</small>`)
                    .join('<br>')
                : '';
            
            li.innerHTML = `
                <div class="threat-content">
                    <div class="threat-header">
                        <span class="primary-prediction">${threat.category}</span>
                        <span class="threat-time">${new Date().toLocaleString()}</span>
                    </div>
                    <p class="threat-description">${threat.threat}</p>
                    ${confidenceHtml ? `<div class="confidence-scores">${confidenceHtml}</div>` : ''}
                    <div class="threat-footer">
                        <small class="hash">Hash: ${threat.hash}</small>
                    </div>
                </div>
            `;
            threatList.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading threats:', error);
        const threatList = document.getElementById('threatList');
        threatList.innerHTML = '<li class="error">Error loading threats. Please try again.</li>';
    }
}

// Load threats when the page loads
document.addEventListener('DOMContentLoaded', loadThreats); 