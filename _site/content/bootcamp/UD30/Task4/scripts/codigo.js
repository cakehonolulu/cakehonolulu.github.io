var valores = [true, 5, false, "hola", "adios", 2];

if (valores[3].length > valores[4].length) {
    console.log(valores[3] + "'s size > than " + valores[4]);
} else if (valores[3].length < valores[4].length) {
    console.log(valores[3] + "'s size < than " + valores[4]);
} else if (valores[3].length == valores[4].length) {
    console.log(valores[3] + "'s size == " + valores[4] + "'s size");
}

if (valores[0])
{
    console.log("Array value 1 is true");
} else {
    console.log("Array value 1 is false");
}

if (valores[2])
{
    console.log("Array value 3 is true");
} else {
    console.log("Array value 3 is false");
}

console.log("Addition: " + (valores[1] + valores[5]));
console.log("Subtraction: " + (valores[1] - valores[5]));
console.log("Multiplication: " + (valores[1] * valores[5]));
console.log("Division: " + (valores[1] / valores[5]));
console.log("Modulus: " + (valores[1] % valores[5]));