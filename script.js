window.addEventListener("load", (event) => {
  new cursoreffects.rainbowCursor();
});


let audious = document.querySelectorAll("audio");


function mutePage() {
    audious.forEach((elem) => elem.pause());
}

function loadAllAudio() {
	audious.forEach((elem) => elem.load());
}

function playNewAudio(name) {
	if (document.getElementById(name).paused) {
		mutePage();
		document.getElementById(name).play();
	} else {
		mutePage();
	}
}
