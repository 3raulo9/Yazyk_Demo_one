// Get the element you want to modify
const jumpingImage = document.querySelector('.logo-img');

// Function to set a random delay and play the animation once
function playAnimationOnce() {
    const randomDelay = Math.floor(Math.random() * 15000); // Random delay between 0 and 15 seconds (15000 milliseconds)
    
    // Check if the animation is currently paused before starting a new one
    if (jumpingImage.style.animationPlayState === 'paused' || jumpingImage.style.animationPlayState === '') {
        jumpingImage.style.animationPlayState = 'running'; // Start the animation only if it's paused or not started
        jumpingImage.style.animationDelay = `${randomDelay}ms`; // Set a positive delay to start at a random point in the animation sequence

        // Set a timeout to stop the animation after it plays once
        setTimeout(() => {
            jumpingImage.style.animationPlayState = 'paused'; // Pause the animation after it plays once
            setTimeout(playAnimationOnce, Math.floor(Math.random() * 170)); // Set a new timeout for the next animation play, adjusting the time to your desired frequency
        }, 1100); // Assuming the animation duration is 1 second (1000 milliseconds), add a bit more time before resetting
    } else {
        setTimeout(playAnimationOnce, 1000); // If the animation is already playing, check again after 1 second
    }
}

// Initially play the animation once
playAnimationOnce();
