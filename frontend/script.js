// Auto-refresh countdown timer - linked from frontend/styles.js
// REFRESH_SECONDS is set globally by styles.py before loading this script
if (typeof REFRESH_SECONDS === 'undefined') {
    var REFRESH_SECONDS = 30; // default value
}
var countdown = REFRESH_SECONDS;
var interval = setInterval(function() {
    countdown--;
    if (countdown <= 0) {
        countdown = REFRESH_SECONDS;
    }
    var el = document.getElementById('countdown-display');
    if (el) {
        el.innerText = countdown;
    }
}, 1000);
