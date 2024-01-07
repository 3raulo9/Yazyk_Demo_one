// Get the image element
var img = document.querySelector('.logo-img');

// Function to add animation class
function animateImage() {
    img.classList.add('animate');

    // Remove the class after animation completes
    img.addEventListener('animationend', function() {
        img.classList.remove('animate');
        setRandomInterval();
    }, {once: true});
}

// Function to set a random interval
function setRandomInterval() {
    var randomTime = Math.random() * 8000; // Random time in milliseconds between 0 and 60000 (60 seconds)
    setTimeout(animateImage, randomTime);
}

// Initial invocation
setRandomInterval();
