// ================= INIT =================
function initPage(){
    loadChart();
}


// ================= LOAD CHART =================
async function loadChart() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();

        const ctx = document.getElementById('attendanceChart').getContext('2d');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Attendance Count',
                    data: data.values,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: 'white' }
                    },
                    y: {
                        ticks: { color: 'white' }
                    }
                }
            }
        });

    } catch (err) {
        console.error(err);
        console.log("Chart loading failed");
    }
}


// ================= AUTO REFRESH =================
// refresh chart every 10 seconds
setInterval(loadChart, 10000);