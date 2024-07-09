document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    function fetchLogs(logType) {
        fetch(`/get_logs/${logType}`)
            .then(response => response.json())
            .then(data => {
                const logsBody = document.getElementById(`${logType}-logs-body`);
                logsBody.innerHTML = "";
                data.logs.forEach(log => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${log.username}</td>
                        <td>${log.action}</td>
                        <td>${log.details}</td>
                        <td>${new Date(log.timestamp).toLocaleString()}</td>
                    `;
                    logsBody.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching logs:', error));
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));

            this.classList.add('active');
            document.getElementById(this.dataset.tab + '-logs').classList.add('active');

            fetchLogs(this.dataset.tab);
        });
    });

    // Fetch initial logs for the active tab
    fetchLogs('alert');

    // Handle theme changes
    document.getElementById('light-theme').addEventListener('click', function () {
        fetch('/change_theme/light', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.body.classList.remove('dark');
                    document.body.classList.add('light');
                }
            });
    });

    document.getElementById('dark-theme').addEventListener('click', function () {
        fetch('/change_theme/dark', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.body.classList.remove('light');
                    document.body.classList.add('dark');
                }
            });
    });

    // Handle language changes
    document.getElementById('en-lang').addEventListener('click', function () {
        fetch('/change_language/en', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                }
            });
    });

    document.getElementById('pt-lang').addEventListener('click', function () {
        fetch('/change_language/pt', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                }
            });
    });
});
