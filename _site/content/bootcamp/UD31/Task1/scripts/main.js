function main() {
    // The random dice numbers
    var firstRng, secondRng;

    // The results array, max combination is 6 by 6
    var results = new Array((6 + 6) + 1);

    // memset to 0
    for (var i = 0; i < results.length; i++) {
        results[i] = 0;
    }

    // Do 36 thousand times
    for (var i = 0; i < 36000; i++) {
        // 2 random numbers between 1-6
        firstRng = Math.floor(Math.random() * (6 - 1 + 1) + 1);
        secondRng = Math.floor(Math.random() * (6 - 1 + 1) + 1);

        // Index the previous array ++
        results[firstRng + secondRng]++;
    }

    // Print the results, exclude 0 and 1 since they can't be obtained
    for (var i = 2; i < results.length; i++) {
        console.log(i + ": " + results[i]);
    }
    
}
