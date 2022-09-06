
function calcStringInfo() {
    var stringToCheck = document.getElementById('string').value.toString();

    alert(checkString(stringToCheck));
}

function checkString(stringToCheck) {
    var hasUppercase = false;
    var hasLowercase = false;
    var char = '';

    var i = 0;

    while (i < stringToCheck.length) {
        char = stringToCheck.charAt(i);

        if (char == char.toUpperCase()) {
            hasUppercase = true;
        }

        if (char == char.toLowerCase()) {
            hasLowercase = true;
        }

        i++;
    }

    if (hasUppercase && hasLowercase) {
        return "String has a mix of Upper-Lower characters";
    } else if (hasUppercase && !hasLowercase) {
        return "String is formed exclusively w/Uppercase characters";
    } else if (!hasUppercase && hasLowercase) {
        return "String is formed exclusively w/Lowercase characters";
    }
}