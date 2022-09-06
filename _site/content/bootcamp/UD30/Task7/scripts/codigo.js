
function calcFactorial() {
    var number = document.getElementById('number').value;

    for (var i = (number - 1); i >= 1; i--)
    {
        number *= i;
    }

    document.getElementById("result").innerHTML = "The result is: " + number;
}