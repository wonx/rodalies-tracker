function updateTime() {
  var now = new Date();
  var options = {
    timeZone: 'Europe/Madrid',
    hour12: false,
    hour: 'numeric',
    minute: 'numeric',
    second: 'numeric'
  };
  var timeString = now.toLocaleTimeString('en-US', options);
  document.getElementById('clock').innerHTML = timeString;
}

setInterval(updateTime, 1000);