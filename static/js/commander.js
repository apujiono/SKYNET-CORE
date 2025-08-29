function playT800Sound() {
    let audio = new Audio('/static/audio/t800-voice.mp3');
    audio.play();
}

function loadThreatResults() {
    fetch('/api/threat/results')
        .then(response => response.json())
        .then(data => {
            let results = document.getElementById('threat-results');
            results.innerHTML = data.map(r => `<p>${r.domain}: ${r.is_terminator || r.score > 80 ? 'Bahaya' : 'Aman'} (Skor ${r.score.toFixed(0)}%)</p>`).join('');
        });
}

function loadAgentStatus() {
    fetch('/agent')
        .then(response => response.json())
        .then(data => {
            document.getElementById('agent-status').innerHTML = `Aktif: ${data.length} T-800 melindungi keluarga.`;
        });
}

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
        .catch(() => alert('Error: Pengecekan gagal.'));
}

function replicateAgent() {
    playT800Sound();
    fetch('/api/replicate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parent_id: 'root', priority: 'scan' })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'replicated') {
                alert(`T-800 baru aktif: ${data.agent_id}`);
                loadAgentStatus();
            }
        });
}

loadThreatResults();
loadAgentStatus();