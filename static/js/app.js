// API Base URL
const API_URL = 'http://localhost:5000/api';

// Current risk being edited
let currentRiskId = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadRisks();
    loadStats();
});

// ========== Load Risks ==========
async function loadRisks() {
    try {
        const response = await fetch(`${API_URL}/risks`);
        const risks = await response.json();
        allRisks = risks; // Store for filtering

        displayRisks(risks);
        renderHeatMap(risks);
    } catch (error) {
        showToast('Error loading risks: ' + error.message, 'error');
    }
}

// ========== Display Risks in Table ==========
function displayRisks(risks) {
    const tbody = document.getElementById('risk-table-body');

    if (risks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="no-data">No risks found. Click "Add Risk" to get started.</td></tr>';
        return;
    }

    tbody.innerHTML = risks.map(risk => {
        const severity = getSeverity(risk.score);
        const severityClass = `severity-${severity.toLowerCase()}`;
        const controls = risk.controls.length > 0 ? risk.controls.join(', ') : 'None';

        return `
            <tr>
                <td>${risk.id}</td>
                <td><strong>${risk.name}</strong><br><small style="color: #6C757D;">${risk.description || 'N/A'}</small></td>
                <td><span class="badge badge-framework">${risk.framework ? risk.framework.toUpperCase() : 'SOC2'}</span></td>
                <td style="text-align: center;">${risk.likelihood}</td>
                <td style="text-align: center;">${risk.impact}</td>
                <td style="text-align: center;"><strong>${risk.score}</strong></td>
                <td><span class="severity-badge ${severityClass}">${severity}</span></td>
                <td><small>${controls}</small></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-secondary btn-small" onclick="editRisk(${risk.id})">Edit</button>
                        <button class="btn btn-danger btn-small" onclick="deleteRisk(${risk.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Global chart instances
let statusChart = null;
let ownerChart = null;

// ========== Load Statistics ==========
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const stats = await response.json();

        // Update Key Metrics
        document.getElementById('total-risks').textContent = stats.total;
        document.getElementById('critical-risks').textContent = stats.critical;
        document.getElementById('high-risks').textContent = stats.high;
        document.getElementById('medium-risks').textContent = stats.medium;
        document.getElementById('low-risks').textContent = stats.low;

        // Render Charts & Lists
        renderCharts(stats);
        renderTopRisks(stats.top_risks);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function renderCharts(stats) {
    // 1. Status Chart (Doughnut)
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    const statusLabels = Object.keys(stats.by_status);
    const statusData = Object.values(stats.by_status);

    if (statusChart) statusChart.destroy();

    statusChart = new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: statusLabels,
            datasets: [{
                data: statusData,
                backgroundColor: ['#28A745', '#FFC107', '#17A2B8', '#6C757D'], // Green, Yellow, Teal, Gray
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // 2. Owner Chart (Bar)
    const ownerCtx = document.getElementById('ownerChart').getContext('2d');
    const ownerLabels = Object.keys(stats.by_owner);
    const ownerData = Object.values(stats.by_owner);

    if (ownerChart) ownerChart.destroy();

    ownerChart = new Chart(ownerCtx, {
        type: 'bar',
        data: {
            labels: ownerLabels,
            datasets: [{
                label: 'Risks per Owner',
                data: ownerData,
                backgroundColor: '#0066CC',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });

    // 3. Framework Chart (Polar Area)
    const frameworkCtx = document.getElementById('frameworkChart').getContext('2d');
    const frameworkLabels = Object.keys(stats.by_framework || {});
    const frameworkData = Object.values(stats.by_framework || {});

    if (window.frameworkChartInstance) window.frameworkChartInstance.destroy();

    window.frameworkChartInstance = new Chart(frameworkCtx, {
        type: 'polarArea',
        data: {
            labels: frameworkLabels,
            datasets: [{
                data: frameworkData,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' }
            },
            scales: {
                r: { ticks: { display: false } }
            }
        }
    });
}

// Global risks array for filtering
let allRisks = [];

// ========== Filter Risks ==========
function filterRisks(framework) {
    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        if (tab.dataset.framework === framework) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    // Filter data
    if (framework === 'all') {
        displayRisks(allRisks);
    } else {
        const filtered = allRisks.filter(r => (r.framework || 'soc2') === framework);
        displayRisks(filtered);
    }
}

function renderTopRisks(risks) {
    const container = document.getElementById('top-risks-list');
    if (!risks || risks.length === 0) {
        container.innerHTML = '<p class="no-data">No critical risks found.</p>';
        return;
    }

    container.innerHTML = risks.map(risk => `
        <div class="top-risk-item">
            <div class="top-risk-info">
                <span class="top-risk-name">${risk.name}</span>
                <span class="top-risk-meta">Owner: ${risk.owner || 'Unassigned'} | Status: ${risk.status}</span>
            </div>
            <div class="top-risk-score">${risk.score}</div>
        </div>
    `).join('');
}

// ========== Get Severity Level ==========
function getSeverity(score) {
    if (score >= 20) return 'Critical';
    if (score >= 15) return 'High';
    if (score >= 10) return 'Medium';
    return 'Low';
}

// ========== Modal Functions ==========
function openAddModal() {
    currentRiskId = null;
    document.getElementById('modal-title').textContent = 'Add New Risk';
    document.getElementById('risk-form').reset();
    document.getElementById('risk-id').value = '';
    document.getElementById('risk-modal').classList.add('show');
}

function closeModal() {
    document.getElementById('risk-modal').classList.remove('show');
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('risk-modal');
    if (event.target === modal) {
        closeModal();
    }
}

// ========== Edit Risk ==========
async function editRisk(riskId) {
    try {
        const response = await fetch(`${API_URL}/risks/${riskId}`);
        const risk = await response.json();

        currentRiskId = riskId;
        document.getElementById('modal-title').textContent = 'Edit Risk';
        document.getElementById('risk-id').value = risk.id;
        document.getElementById('risk-name').value = risk.name;
        document.getElementById('risk-description').value = risk.description || '';
        document.getElementById('risk-framework').value = risk.framework || 'soc2';
        document.getElementById('risk-likelihood').value = risk.likelihood;
        document.getElementById('risk-impact').value = risk.impact;
        document.getElementById('risk-treatment').value = risk.treatment || 'Mitigate';
        document.getElementById('risk-action-items').value = risk.action_items || '';
        document.getElementById('risk-owner').value = risk.owner || '';
        document.getElementById('risk-due-date').value = risk.due_date || '';
        document.getElementById('risk-status').value = risk.status || 'Open';

        document.getElementById('risk-modal').classList.add('show');
    } catch (error) {
        showToast('Error loading risk: ' + error.message, 'error');
    }
}

// ========== Save Risk ==========
async function saveRisk(event) {
    event.preventDefault();

    const riskData = {
        name: document.getElementById('risk-name').value,
        description: document.getElementById('risk-description').value,
        likelihood: parseInt(document.getElementById('risk-likelihood').value),
        impact: parseInt(document.getElementById('risk-impact').value),
        framework: document.getElementById('risk-framework').value,
        treatment: document.getElementById('risk-treatment').value,
        action_items: document.getElementById('risk-action-items').value,
        owner: document.getElementById('risk-owner').value,
        due_date: document.getElementById('risk-due-date').value || null,
        status: document.getElementById('risk-status').value
    };

    try {
        let response;

        if (currentRiskId) {
            // Update existing risk
            response = await fetch(`${API_URL}/risks/${currentRiskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(riskData)
            });
        } else {
            // Add new risk
            response = await fetch(`${API_URL}/risks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(riskData)
            });
        }

        if (response.ok) {
            showToast(currentRiskId ? 'Risk updated successfully!' : 'Risk added successfully!');
            closeModal();
            loadRisks();
            loadStats();
        } else {
            const error = await response.json();
            showToast('Error: ' + error.error, 'error');
        }
    } catch (error) {
        showToast('Error saving risk: ' + error.message, 'error');
    }
}

// ========== Delete Risk ==========
async function deleteRisk(riskId) {
    if (!confirm('Are you sure you want to delete this risk?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/risks/${riskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Risk deleted successfully!');
            loadRisks();
            loadStats();
        } else {
            showToast('Error deleting risk', 'error');
        }
    } catch (error) {
        showToast('Error deleting risk: ' + error.message, 'error');
    }
}

// ========== Export Risks ==========
async function exportRisks(format) {
    try {
        const response = await fetch(`${API_URL}/export/${format}`);

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `risk_register.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showToast(`Risk register exported as ${format.toUpperCase()}`);
        } else {
            const error = await response.json();
            showToast('Error exporting: ' + error.error, 'error');
        }
    } catch (error) {
        showToast('Error exporting risks: ' + error.message, 'error');
    }
}

// ========== Toast Notification ==========
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast show';

    if (type === 'error') {
        toast.classList.add('error');
    }

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ========== Risk Heat Map ==========
function renderHeatMap(risks) {
    const grid = document.getElementById('heat-map-grid');

    // Create 5x5 grid (likelihood 5-1 from top to bottom, impact 1-5 from left to right)
    const matrix = {};

    // Initialize all cells with 0 count
    for (let likelihood = 5; likelihood >= 1; likelihood--) {
        for (let impact = 1; impact <= 5; impact++) {
            const key = `${likelihood}-${impact}`;
            matrix[key] = { count: 0, risks: [] };
        }
    }

    // Populate matrix with actual risks
    risks.forEach(risk => {
        const key = `${risk.likelihood}-${risk.impact}`;
        if (matrix[key]) {
            matrix[key].count++;
            matrix[key].risks.push(risk);
        }
    });

    // Generate grid cells (top to bottom, left to right)
    let html = '';
    for (let likelihood = 5; likelihood >= 1; likelihood--) {
        for (let impact = 1; impact <= 5; impact++) {
            const key = `${likelihood}-${impact}`;
            const cellData = matrix[key];
            const score = likelihood * impact;
            const zone = getZoneClass(score);
            const isEmpty = cellData.count === 0;

            // Create tooltip with risk names
            let tooltip = '';
            if (cellData.risks.length > 0) {
                const riskNames = cellData.risks.map(r => r.name).join(', ');
                tooltip = `<div class="heat-cell-tooltip">${riskNames}</div>`;
            }

            html += `
                <div class="heat-cell ${zone} ${isEmpty ? 'empty' : ''}" 
                     data-likelihood="${likelihood}" 
                     data-impact="${impact}"
                     data-score="${score}">
                    <div class="risk-count">${cellData.count}</div>
                    <div class="cell-coordinates">L${likelihood} × I${impact}</div>
                    ${tooltip}
                </div>
            `;
        }
    }

    grid.innerHTML = html;
}

// Get color zone class based on risk score
function getZoneClass(score) {
    if (score >= 20) return 'zone-critical';
    if (score >= 15) return 'zone-high';
    if (score >= 10) return 'zone-medium';
    return 'zone-low';
}
