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
});
