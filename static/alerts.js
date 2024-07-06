const socket = io.connect('http://' + document.domain + ':' + location.port);

function updateAlertsTable(alerts) {
    const tableDiv = document.getElementById('alerts-table');
    tableDiv.innerHTML = `
        <table class="alerts-table">
            <tr>
                <th>Ticker</th>
                <th>Condition</th>
                <th>Price</th>
                <th>Action</th>
            </tr>
        </table>
    `;

    const table = tableDiv.querySelector('.alerts-table');

    alerts.forEach(alert => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${alert.ticker_symbol}</td>
            <td>${alert.condition}</td>
            <td>${alert.price}</td>
            <td><form action="/remove_alert/${alert.ticker_symbol}" method="post"><button type="submit">Remove</button></form></td>
        `;
        table.appendChild(row);
    });
}

socket.on('connect', () => {
    console.log('Connected to the server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from the server');
});

socket.on('new_alert', data => {
    console.log("New alert received:", data);
    location.reload();
});

socket.on('remove_alert', data => {
    console.log("Alert removed:", data);
    location.reload();
});

socket.on('update_alerts', alerts => {
    updateAlertsTable(alerts);
});

document.addEventListener('DOMContentLoaded', () => {
    fetch('/get_alerts')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateAlertsTable(data.alerts);
        })
        .catch(error => {
            console.error('Error fetching alerts:', error);
        });
});

socket.on('price_alert', data => {
    console.log("Price alert received:", data);
    Swal.fire({
        title: 'Price Alert',
        text: data.message,
        icon: 'info',
        confirmButtonText: 'OK'
    });
});