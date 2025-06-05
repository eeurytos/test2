let chart;

async function fetchData() {
    const resp = await fetch('/api/holdings');
    const data = await resp.json();
    updateChart(data);
}

async function addAsset() {
    const asset = document.getElementById('asset').value;
    const amount = parseFloat(document.getElementById('amount').value);
    if (!amount) return;
    await fetch('/api/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({asset, amount})
    });
    document.getElementById('amount').value = '';
    fetchData();
}

async function removeAsset() {
    const asset = document.getElementById('asset').value;
    const amount = parseFloat(document.getElementById('amount').value);
    if (!amount) return;
    await fetch('/api/remove', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({asset, amount})
    });
    document.getElementById('amount').value = '';
    fetchData();
}

function updateChart(data) {
    const labels = Object.keys(data.holdings);
    const values = labels.map(l => data.holdings[l].value_try);
    document.getElementById('total').innerText = 'Total TRY: ' + data.total_try.toFixed(2);
    if (chart) chart.destroy();
    const ctx = document.getElementById('chart');
    chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{data: values}]
        },
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const asset = labels[context.dataIndex];
                            const amt = data.holdings[asset].amount;
                            return asset + ': ' + amt + ' (' + values[context.dataIndex].toFixed(2) + ' TRY)';
                        }
                    }
                }
            }
        }
    });
}

fetchData();
setInterval(fetchData, 2000);
