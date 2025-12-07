// API Base URL
const API_URL = 'http://localhost:5000/api';

// Current risk being edited
let currentRiskId = null;
let currentAuditType = 'type1'; // Default to Type 1

// Mock SOC 2 Data - Professional & Realistic
const READINESS_CHECKLIST = {
    type1: [
        { id: 1, text: "CC1.1 - Values & Ethics: Code of Conduct published & signed", completed: true },
        { id: 2, text: "CC2.1 - Communication: Infosec policies approved by mgmt", completed: true },
        { id: 3, text: "CC3.1 - Risk Assessment: Annual RA report finalized", completed: true },
        { id: 4, text: "CC5.1 - Logical Access: MFA enforced on all critical systems (config screenshot)", completed: true },
        { id: 5, text: "CC6.1 - Security Operations: Vulnerability Scan (clean report)", completed: true },
        { id: 6, text: "CC7.1 - Vendor Mgmt: Critical vendor list defined", completed: true },
        { id: 7, text: "CC9.1 - Risk Mitigation: Cyber insurance policy active", completed: false }
    ],
    type2: [
        { id: 8, text: "CC1.4 - Background Checks: Sample of 5 new hires (evidence of check)", completed: false },
        { id: 9, text: "CC5.2 - User Access Reviews: Quarterly review logs (Q1-Q3)", completed: false },
        { id: 10, text: "CC6.8 - Change Management: Sample of 25 changes (tickets + approval)", completed: false },
        { id: 11, text: "CC7.2 - Incident Response: Tabletop exercise completion (annual)", completed: true },
        { id: 12, text: "CC8.1 - Patch Management: Patch logs for audit period", completed: true },
        { id: 13, text: "CC4.1 - Monitoring: Evidence of 24/7 alert monitoring logs", completed: false },
        { id: 14, text: "CC5.3 - Offboarding: Revocation evidence for terminated users", completed: false }
    ]
};

const EVIDENCE_REQUIRED = {
    type1: [
        { icon: "📄", name: "InfoSec_Policies_Signed_v2024.pdf", type: "Policy" },
        { icon: "👥", name: "Org_Chart_&_Roles.pdf", type: "Admin" },
        { icon: "🔒", name: "AWS_MFA_Config_Screenshot.png", type: "Config" },
        { icon: "🛡️", name: "Recent_PenTest_Report_Clean.pdf", type: "Report" },
        { icon: "📋", name: "Risk_Assessment_2024.xslx", type: "Risk" }
    ],
    type2: [
        { icon: "🎫", name: "Jira_Change_Tickets_Population.csv", type: "List" },
        { icon: "📝", name: "Access_Review_Signoffs_Q1_Q2_Q3.pdf", type: "Review" },
        { icon: "🚫", name: "Terminated_User_Revocation_Samples.zip", type: "Sample" },
        { icon: "☁️", name: "CloudTrail_Logs_Integrity_Check.json", type: "Log" },
        { icon: "🎓", name: "Security_Awareness_Training_Completion.csv", type: "HR" }
    ]
};

// Trust Service Criteria Data (Mock)
const TSC_DATA = {
    labels: ['Security (Common Criteria)', 'Availability', 'Confidentiality', 'Processing Integrity', 'Privacy'],
    data: [12, 5, 8, 3, 4] // Example distribution
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadRisks();
    loadStats();
    toggleAuditType('type1'); // Init SOC 2 View
});

// ========== Tab Switching ==========
function switchTab(tabId) {
    // Hide all views
    document.querySelectorAll('.dashboard-section').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    // Show selected view
    document.getElementById(`view-${tabId}`).style.display = 'block';

    // Activate button
    // Find button that calls this tabId
    const buttons = document.getElementsByClassName('tab-btn');
    for (let btn of buttons) {
        if (btn.getAttribute('onclick').includes(tabId)) {
            btn.classList.add('active');
        }
    }
}

// ========== SOC 2 Audit Type Toggle ==========
function toggleAuditType(type) {
    currentAuditType = type;

    // update descriptions
    document.querySelectorAll('.audit-desc').forEach(el => el.classList.remove('active'));
    document.getElementById(`audit-desc-${type}`).classList.add('active');

    updateReadinessChecklist(type);
    updateEvidenceList(type);
}

function updateReadinessChecklist(type) {
    const list = READINESS_CHECKLIST[type];
    const container = document.getElementById('checklist-container');
    const completedCount = list.filter(i => i.completed).length;
    const total = list.length;
    const percentage = Math.round((completedCount / total) * 100);

    document.getElementById('readiness-progress').textContent = `${percentage}% Ready`;

    container.innerHTML = list.map(item => `
        <div class="checklist-item ${item.completed ? 'completed' : ''}">
            <input type="checkbox" ${item.completed ? 'checked' : ''} disabled>
            <span class="checklist-label">${item.text}</span>
        </div>
    `).join('');
}

function updateEvidenceList(type) {
    const list = EVIDENCE_REQUIRED[type];
    const container = document.getElementById('evidence-list');
    document.getElementById('evidence-badge').textContent = type === 'type1' ? 'Snapshot' : 'Continuous';

    container.innerHTML = list.map(item => `
        <li class="evidence-item">
            <div class="evidence-name">${item.name}</div>
        </li>
    `).join('');
}

// ========== Load Risks (Filtered for SOC 2 implicitly) ==========
async function loadRisks() {
    try {
        const response = await fetch(`${API_URL}/risks`);
        const risks = await response.json();

        // In a real app we might filter by framework='soc2', but for this view we assume all are relevant or just show all
        allRisks = risks;
        displayRisks(risks);
        allRisks = risks;
        displayRisks(risks);

        // Render Scanner Dashboard Stats if risks are loaded
        renderScannerDashboard(risks);
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
        // Map generic categories or assume Common Criteria if not specified
        const tscCategory = risk.category || "Security (CC)";

        return `
            <tr>
                <td>${risk.id}</td>
                <td><strong>${risk.name}</strong><br><small style="color: #6C757D;">${risk.description || 'N/A'}</small></td>
                <td><span class="badge badge-framework">${tscCategory}</span></td>
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
let tscChart = null;
let gapChart = null;

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

        // Render SOC 2 Charts
        renderSoc2Charts(stats);
        renderTopRisks(stats.top_risks);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function renderSoc2Charts(stats) {
    // 1. Risks by Trust Service Criteria (TSC)
    const tscCtx = document.getElementById('tscChart').getContext('2d');
    if (tscChart) tscChart.destroy();

    tscChart = new Chart(tscCtx, {
        type: 'doughnut',
        data: {
            labels: TSC_DATA.labels,
            datasets: [{
                data: TSC_DATA.data,
                backgroundColor: ['#4A90E2', '#50E3C2', '#F5A623', '#D0021B', '#9013FE'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' }
            }
        }
    });

    // 2. Control Gap Analysis (Mocked for visual)
    const gapCtx = document.getElementById('gapChart').getContext('2d');
    if (gapChart) gapChart.destroy();

    gapChart = new Chart(gapCtx, {
        type: 'bar',
        data: {
            labels: ['Security', 'Availability', 'Confidentiality', 'Processing Integrity', 'Privacy'],
            datasets: [
                {
                    label: 'Implemented Controls',
                    data: [25, 10, 15, 5, 8],
                    backgroundColor: '#28A745'
                },
                {
                    label: 'Missing/Gap',
                    data: [5, 2, 8, 3, 4],
                    backgroundColor: '#DC3545'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { stacked: true },
                y: { beginAtZero: true, stacked: true }
            }
        }
    });
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
    document.getElementById('modal-title').textContent = 'Add SOC 2 Risk';
    document.getElementById('risk-form').reset();
    document.getElementById('risk-id').value = '';
    // Default framework to SOC 2 (hidden input)
    document.getElementById('risk-framework').value = 'soc2';
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
        framework: 'soc2', // Enforce SOC 2
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

// ========== Render Scanner Dashboard Statistics ==========
function renderScannerDashboard(risks) {
    if (!risks || risks.length === 0) {
        return;
    }

    // Group risks by scanner_type
    const scannerTypes = {
        'Vulnerability Scanner': [],
        'Cloud Configuration': [],
        'Dependency Scanner': [],
        'Attack Surface Scanner': []
    };

    risks.forEach(risk => {
        const scannerType = risk.scanner_type || 'Manual';
        if (scannerTypes[scannerType]) {
            scannerTypes[scannerType].push(risk);
        }
    });

    // Update Vulnerability Scanner
    updateScannerCard('vuln', scannerTypes['Vulnerability Scanner']);

    // Update Cloud Config Scanner
    updateScannerCard('cloud', scannerTypes['Cloud Configuration']);

    // Update Dependency Scanner
    updateScannerCard('dep', scannerTypes['Dependency Scanner']);

    // Update Attack Surface Scanner
    updateScannerCard('attack', scannerTypes['Attack Surface Scanner']);
}

function updateScannerCard(prefix, risks) {
    const severityCounts = {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
    };

    let highRiskCount = 0;
    let totalCount = risks.length;

    risks.forEach(r => {
        const score = r.score || (r.likelihood * r.impact);
        if (score >= 20) {
            severityCounts.critical++;
            highRiskCount++;
        } else if (score >= 15) {
            severityCounts.high++;
            highRiskCount++;
        } else if (score >= 10) {
            severityCounts.medium++;
        } else {
            severityCounts.low++;
        }
    });

    // Update metrics
    const highEl = document.getElementById(`cnt-${prefix}-high`);
    const totalEl = document.getElementById(`cnt-${prefix}-total`);

    if (highEl) highEl.textContent = highRiskCount;
    if (totalEl) totalEl.textContent = totalCount;

    // Render donut chart
    const chartId = `${prefix}ScannerChart`;
    const canvas = document.getElementById(chartId);
    if (!canvas) return;

    const existingChart = Chart.getChart(chartId);
    if (existingChart) existingChart.destroy();

    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [
                    severityCounts.critical,
                    severityCounts.high,
                    severityCounts.medium,
                    severityCounts.low
                ],
                backgroundColor: ['#DC3545', '#FF6B35', '#FFC107', '#28A745'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '65%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
            }
        }
    });
}

// Render Comprehensive SOC 2 Charts
function renderSoc2Charts(stats, risks) {
    // Darker text for light mode (#0f172a), lighter for dark mode (#cbd5e1)
    Chart.defaults.color = document.body.classList.contains('dark-mode') ? '#cbd5e1' : '#0f172a';
    Chart.defaults.borderColor = document.body.classList.contains('dark-mode') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Helper to destroy existing chart if canvas exists
    const destroyChart = (id) => {
        const canvas = document.getElementById(id);
        const chart = Chart.getChart(id);
        if (chart) chart.destroy();
        return canvas;
    };

    // 1. Risk Severity Donut
    destroyChart('severityChart');
    new Chart(document.getElementById('severityChart'), {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [stats.critical, stats.high, stats.medium, stats.low],
                backgroundColor: ['#DC3545', '#FF6B35', '#FFC107', '#28A745'],
                borderWidth: 0
            }]
        },
        options: { cutout: '60%', plugins: { legend: { position: 'right' } } }
    });

    // 2. Risk Status Donut
    const statusCounts = { 'Open': 0, 'In Progress': 0, 'Mitigated': 0, 'Accepted': 0 };
    if (risks && risks.length) {
        risks.forEach(r => {
            if (statusCounts[r.status] !== undefined) statusCounts[r.status]++;
            else statusCounts['Open']++;
        });
    }
    destroyChart('statusChart');
    new Chart(document.getElementById('statusChart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusCounts),
            datasets: [{
                data: Object.values(statusCounts),
                backgroundColor: ['#4A90E2', '#FFC107', '#28A745', '#6C757D'],
                borderWidth: 0
            }]
        },
        options: { cutout: '60%', plugins: { legend: { position: 'right' } } }
    });

    // 3. Risk Heat Map (Bubble Chart)
    destroyChart('heatmapChart');
    const heatData = {};
    if (risks && risks.length) {
        risks.forEach(r => {
            const key = `${r.impact}-${r.likelihood}`;
            if (!heatData[key]) heatData[key] = { x: r.impact, y: r.likelihood, r: 0, count: 0 };
            heatData[key].count++;
            heatData[key].r = 5 + (heatData[key].count * 3);
        });
    }
    new Chart(document.getElementById('heatmapChart'), {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Risks',
                data: Object.values(heatData),
                backgroundColor: (ctx) => {
                    const v = ctx.raw;
                    if (!v) return '#ccc';
                    const score = v.x * v.y;
                    if (score >= 20) return 'rgba(220, 53, 69, 0.7)'; // Critical
                    if (score >= 15) return 'rgba(255, 107, 53, 0.7)'; // High
                    if (score >= 10) return 'rgba(255, 193, 7, 0.7)'; // Medium
                    return 'rgba(40, 167, 69, 0.7)'; // Low
                }
            }]
        },
        options: {
            scales: {
                x: { min: 0, max: 6, title: { display: true, text: 'Impact' }, ticks: { stepSize: 1 } },
                y: { min: 0, max: 6, title: { display: true, text: 'Likelihood' }, ticks: { stepSize: 1 } }
            },
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (ctx) => `Risks: ${ctx.raw.count} (Imp:${ctx.raw.x}, Lik:${ctx.raw.y})` } }
            }
        }
    });

    // 4. Risks by TSC Category
    const tscCounts = { 'Security': 0, 'Availability': 0, 'Confidentiality': 0, 'Processing Integrity': 0, 'Privacy': 0 };
    if (risks && risks.length) {
        risks.forEach(r => {
            const cats = Object.keys(tscCounts);
            const idx = (r.id.charCodeAt(0) + r.id.length) % cats.length; // consistent hash
            tscCounts[cats[idx]]++;
        });
    }
    destroyChart('tscCategoryChart');
    new Chart(document.getElementById('tscCategoryChart'), {
        type: 'polarArea',
        data: {
            labels: Object.keys(tscCounts),
            datasets: [{
                data: Object.values(tscCounts),
                // Solid colors for maximum readability
                backgroundColor: ['#4A90E2', '#50E3C2', '#B8E986', '#BD10E0', '#F5A623']
            }]
        },
        options: { scales: { r: { suggestedMin: 0 } }, plugins: { legend: { position: 'right' } } }
    });

    // 5. Risks by Owner
    const ownerCounts = {};
    if (risks && risks.length) {
        risks.forEach(r => {
            const owner = r.owner || 'Unassigned';
            ownerCounts[owner] = (ownerCounts[owner] || 0) + 1;
        });
    }
    destroyChart('ownerChart');
    new Chart(document.getElementById('ownerChart'), {
        type: 'bar',
        data: {
            labels: Object.keys(ownerCounts),
            datasets: [{
                label: 'Risks',
                data: Object.values(ownerCounts),
                backgroundColor: '#4A90E2',
                borderRadius: 4
            }]
        },
        options: { indexAxis: 'y', plugins: { legend: { display: false } } }
    });

    // 6. Control Coverage (Gauge Chart)
    destroyChart('coverageChart');

    // Calculate Dynamic Score: (Mitigated Risks / Total Risks) * 10
    let totalRisks = risks ? risks.length : 0;
    let mitigatedRisks = risks ? risks.filter(r => r.status === 'Mitigated').length : 0;
    let coverageScore = totalRisks > 0 ? (mitigatedRisks / totalRisks) * 10 : 0;
    // Round to 1 decimal place
    coverageScore = Math.round(coverageScore * 10) / 10;

    // Gauge Needle Plugin
    const gaugeNeedle = {
        id: 'gaugeNeedle',
        afterDatasetDraw(chart, args, options) {
            const { ctx, config, data, chartArea: { top, bottom, left, right, width, height } } = chart;

            ctx.save();
            const needleValue = data.datasets[0].needleValue;
            const dataTotal = data.datasets[0].data.reduce((a, b) => a + b, 0);
            const angle = Math.PI + (1 / dataTotal * needleValue * Math.PI);
            const cx = width / 2;
            const cy = chart._metasets[0].data[0].y;

            // Needle
            ctx.translate(cx, cy);
            ctx.rotate(angle);
            ctx.beginPath();
            ctx.moveTo(0, -2);
            ctx.lineTo(height / 2 - 20, 0); // length
            ctx.lineTo(0, 2);
            ctx.fillStyle = document.body.classList.contains('dark-mode') ? '#eee' : '#444';
            ctx.fill();

            // Needle Dot
            ctx.translate(-cx, -cy);
            ctx.beginPath();
            ctx.arc(cx, cy, 5, 0, 10);
            ctx.fillStyle = document.body.classList.contains('dark-mode') ? '#eee' : '#444';
            ctx.fill();
            ctx.restore();

            // Text "5/10"
            ctx.font = 'bold 30px sans-serif';
            ctx.fillStyle = document.body.classList.contains('dark-mode') ? '#fff' : '#333';
            ctx.textAlign = 'center';
            ctx.fillText(`${needleValue}/10`, cx, top + 40);
        }
    };

    new Chart(document.getElementById('coverageChart'), {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'Bad', 'Average', 'Good', 'Excellent'],
            datasets: [{
                data: [2, 2, 2, 2, 2], // 5 equal segments
                backgroundColor: [
                    '#FF6384', // Red
                    '#FF9F40', // Orange
                    '#FFCD56', // Yellow
                    '#4BC0C0', // Green
                    '#36A2EB'  // Blue/Dark Green
                ],
                needleValue: coverageScore, // Dynamic Value
                borderWidth: 0,
                cutout: '50%',
                circumference: 180,
                rotation: 270,
            }]
        },
        options: {
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            aspectRatio: 1.5
        },
        plugins: [gaugeNeedle]
    });
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
            a.download = `soc2_risk_register.${format}`;
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
