var letras = ['T', 'R', 'W', 'A', 'G', 'M', 'Y', 'F', 'P', 'D', 'X', 'B', 'N', 'J', 'Z', 'S', 'Q', 'V', 'H', 'L', 'C', 'K', 'E', 'T'];

function calcLetter() {
    var numbers = document.getElementById('numbers').value;
    var letter = document.getElementById('letter').value.toString();

    if (numbers > 0 || numbers < 999999999)
    {
        var check = letras[(numbers % 23)];

        if (check === letter.toUpperCase()) {
            alert("The specified letter matches the calculated one!");
        }
        else
        {
            alert("The specified letter doesn't match the calculated one!");
        }
    }
    else
    {
        alert("Invalid DNI Number, check your input!");
    }
}