var firstRun = true;

function clockRun() {
    if (firstRun) {
        setInterval(clockRun, 1000);
        firstRun = false;
    }

    currentDate = new Date();

    document.getElementById('hour').innerHTML = ('0' + currentDate.getHours()).slice(-2);
    document.getElementById('minute').innerHTML = ('0' + currentDate.getMinutes()).slice(-2);
    document.getElementById('second').innerHTML = ('0' + currentDate.getSeconds()).slice(-2);
}