function calcPalindromity() {
    var stringToCheck = document.getElementById('string').value.toString();

    // Remove whitespaces
    stringToCheck.replaceAll(" ", "");

    // Lowercase the entire string
    stringToCheck.toLowerCase();

    // Reverse the string
    var aux = stringToCheck.split("").reverse().join("");

    // Check for palindromity
    if (stringToCheck === aux) {
        alert("String is a palindrome!");
    } else {
        alert("String isn't a palindrome...");
    }
}