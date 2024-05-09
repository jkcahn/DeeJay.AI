function delayedRedirect() {
    var delay = 2000; // 2 seconds

    setTimeout(function() {
        // redirect to process route to prompt genai
        window.location.href = '/process';
    }, delay);
}