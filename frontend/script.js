// Enhanced dashboard script with countdown, filters, refresh mock
if (typeof REFRESH_SECONDS === 'undefined') {
    var REFRESH_SECONDS = 30;
}

// Countdown timer
var countdown = REFRESH_SECONDS;
var interval = setInterval(function() {
    countdown--;
    if (countdown <= 0) {
        countdown = REFRESH_SECONDS;
        refreshData(); // Auto-refresh
    }
    var el = document.getElementById('countdown-display');
    if (el) el.innerText = countdown;
}, 1000);

// Mock refresh data
function refreshData() {
    console.log('Refreshing dashboard data...');
    // Animate metrics
    document.querySelectorAll('.metric-value').forEach(el => {
        el.style.transform = 'scale(1.05)';
        setTimeout(() => el.style.transform = 'scale(1)', 200);
    });
    // Mock random delta changes
    document.querySelectorAll('.metric-delta').forEach(el => {
        const delta = Math.floor(Math.random() * 20 - 10);
        el.textContent = (delta >= 0 ? '+' : '') + delta + '%';
        el.className = 'metric-delta' + (delta >= 0 ? ' positive' : ' negative');
    });
}

// Filter functionality
document.addEventListener('DOMContentLoaded', function() {
    // Search filter
    const searchInput = document.querySelector('.glass-input[placeholder*="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const term = this.value.toLowerCase();
            // Mock filter rows (extend for real data)
            document.querySelectorAll('.table-placeholder tbody tr').forEach(row => {
                row.style.display = row.textContent.toLowerCase().includes(term) ? '' : 'none';
            });
        });
    }

    // Refresh button
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            countdown = REFRESH_SECONDS;
            refreshData();
        });
    }

    // Clear filters
    const clearBtn = document.querySelector('.clear-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            document.querySelectorAll('.glass-input').forEach(input => {
                input.value = '';
            });
            document.querySelectorAll('.table-placeholder tbody tr').forEach(row => {
                row.style.display = '';
            });
        });
    }
});
