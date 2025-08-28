// Initialize 3D globe (Cesium.js)
Cesium.Ion.defaultAccessToken = 'YOUR_CESIUM_TOKEN';
let viewer = new Cesium.Viewer('map', {
    terrainProvider: Cesium.createWorldTerrain()
});

// Play T-800 sound
function playT800Sound() {
    let audio = new Audio('/static/audio/t800-voice.mp3');
    audio.play();
}

// Load threat results
function loadThreatResults() {
    fetch('/api/threat/results')
        .then(response => response.json())
        .then(data => {
            let results = document.getElementById('threat-results');
            results.innerHTML = '<table><tr><th>Domain</th><th>Status</th><th>Malicious</th><th>Score</th></tr>' +
                data.map(r => `<tr><td>${r.domain}</td><td>${r.is_terminator ? 'Threat' : 'Safe'}</td><td>${r.malicious}</td><td>${r.score.toFixed(2)}</td></tr>`).join('') +
                '</table>';
            data.forEach(r => {
                if (r.is_terminator && r.location) {
                    Cesium.Entity({
                        position: Cesium.Cartesian3.fromDegrees(r.location.lon, r.location.lat),
                        point: { pixelSize: 10, color: Cesium.Color.RED },
                        label: { text: `${r.domain} (${r.score.toFixed(2)})`, font: '14px Orbitron' }
                    });
                }
            });
        });
}

// Load analytics
function loadAnalytics() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            new Chart(document.getElementById('analytics-chart'), {
                type: 'bar',
                data: {
                    labels: ['Total Domains', 'Threats', 'Malicious'],
                    datasets: [{ label: 'Stats', data: [data.total_domains, data.threats, data.malicious], backgroundColor: '#ff0000' }]
                },
                options: { scales: { y: { beginAtZero: true } } }
            });
        });
}

// Scan threat
function scanThreat() {
    playT800Sound();
    let keyword = document.getElementById('keyword').value;
    fetch('/api/threat/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: keyword })
    })
        .then(response => response.json())
        .then(() => loadThreatResults())
        .catch(() => alert('Error: Threat scan failed.'));
}

// Load agent details
function loadAgentDetails() {
    let select = document.getElementById('agent-select');
    let agentId = select.value;
    fetch(`/agent/commands?id=${agentId}`)
        .then(response => response.json())
        .then(data => {
            let details = document.getElementById('agent-details');
            details.innerHTML = data.map(c => `<p>Command: ${c.command} (${c.status})</p>`).join('');
        });
    fetch('/agent')
        .then(response => response.json())
        .then(data => {
            let list = document.getElementById('agent-list');
            list.innerHTML = data.map(a => `<div class="agent-item">${a.data.id} - ${a.status} (Parent: ${a.parent_id || 'Root'}) - Priority: ${a.priority}</div>`).join('');
            // Visualisasi hierarchy
            let hierarchy = d3.hierarchy({ name: 'Skynet', children: data.map(a => ({ name: a.data.id, parent: a.parent_id || 'Skynet' })) });
            d3.tree().size([400, 200])(hierarchy);
        });
}

// Send command
function sendCommand(command) {
    let agentId = document.getElementById('agent-select').value;
    fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId, command: command })
    })
        .then(() => loadAgentDetails())
        .catch(() => alert('Error: Command transmission failed.'));
}

// Replicate agent
function replicateAgent() {
    let agentId = document.getElementById('agent-select').value || 'root';
    fetch('/api/replicate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parent_id: agentId, priority: 'scan' })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'replicated') {
                let list = document.getElementById('agent-list');
                list.innerHTML += `<div class="agent-item new-agent">T-800 spawned: ${data.agent_id} (${data.priority})</div>`;
                playT800Sound();
                setTimeout(() => document.querySelector('.new-agent').classList.remove('new-agent'), 2000);
                loadAgentDetails();
            }
        });
}

// Retaliation (CyberWar)
function retaliate(mode) {
    let target = document.getElementById('retaliate-ip').value;
    fetch('/api/retaliate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target, mode: mode })
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('war-log').innerHTML += `<p>${data.target}: ${data.mode} executed.</p>`;
            playT800Sound();
        });
}

// Dead Man's Switch
function activateSwitch() {
    document.getElementById('switch-modal').style.display = 'block';
}

function confirmSwitch() {
    fetch('/api/deadman/activate', { method: 'POST' })
        .then(() => alert('Dead Man’s Switch activated. Skynet Omega ready.'));
    closeModal();
}

function closeModal() {
    document.getElementById('switch-modal').style.display = 'none';
}

// Toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
}

// Load agents
fetch('/agent')
    .then(response => response.json())
    .then(data => {
        let select = document.getElementById('agent-select');
        select.innerHTML = '<option value="">Pilih T-800</option>' +
            data.map(a => `<option value="${a.data.id}">${a.data.id} (${a.status}) - ${a.priority}</option>`).join('');
    });

// Initial load
loadThreatResults();
loadAnalytics();