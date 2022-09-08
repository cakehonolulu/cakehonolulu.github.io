function write(value) {
    document.getElementById("result").value += value;
}

function equals() {
    var p = document.getElementById("result").value;
    var q = eval(p);
    document.getElementById("result").value = q;
}

function clear() {
    document.getElementById("result").value = "";
}