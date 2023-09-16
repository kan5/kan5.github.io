window.addEventListener("load", (event) => {
  new cursoreffects.rainbowCursor();
});
function muteMe(elem) {
//    elem.muted = true;
    elem.pause();
}

// Try to mute all video and audio elements on the page
function mutePage() {
    document.querySelectorAll("video, audio").forEach((elem) => muteMe(elem));
}