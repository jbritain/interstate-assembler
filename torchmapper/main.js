function updateAudioSource(){
  file = document.getElementById("audioUpload").files[0];
  url = URL.createObjectURL(file);
  document.getElementById("audioSource").src = url;
  document.getElementById("audioPlayer").load();
}

function updateSpeed(){
  let speed = document.getElementById("speedSlider").value;
  speed /= 100;
  document.getElementById("audioPlayer").playbackRate = speed;
  document.getElementById("speedLabel").innerText = `Playback speed: ${speed}x`;
}

let playing = false;
function playPause(){
  if(!playing){
    document.getElementById("audioPlayer").currentTime = document.getElementById("startOffsetSelector").value;
    document.getElementById("audioPlayer").play();
    document.getElementById("playPause").innerText = "⏹";
  } else {
    document.getElementById("playPause").innerText = "⏵";
    document.getElementById("audioPlayer").pause();
  }

  playing = !playing;
}

let ctx;
function init(){
  updateAudioSource();
  updateSpeed();
  ctx = document.getElementById("canvas").getContext("2d");
  renderCanvas();
}

function renderCanvas(){
  const height = document.getElementById("canvas").height;
  const width = document.getElementById("canvas").width;

  ctx.clearRect(0, 0, width, height); // clear canvas

  // draw horizontal line across centre
  ctx.fillStyle = "#42f548";
  ctx.fillRect(0, (height / 2), width, 1);

  // draw vertical line down centre
  ctx.fillStyle = "#888888";
  ctx.fillRect(width / 4, 0, 1, height);

  ctx.fillStyle = "#ff33e0";

  let audioPosition = document.getElementById("audioPlayer").currentTime;
  // 64 pixels per second
  let offset = audioPosition * 64;

  beats.forEach(b => {
    let startHeight = 0;
    let endHeight = height;
    switch(b.side){
      
      case "l":
        startHeight = 0;
        endHeight = height / 2;
      case "r":
        startHeight = height / 2;
        endHeight = height;
    }

    ctx.fillRect(b.time * 64 - offset + width / 4, startHeight, 1, endHeight - startHeight);
  });

}

function drawLoop(){
  setTimeout(() => {
    renderCanvas();
    drawLoop();
  }, 10);
}

drawLoop();
