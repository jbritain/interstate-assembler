function updateAudioSource(){
  file = document.getElementById("audioUpload").files[0];
  if(!file){
    return;
  }
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

function updateAudioPosition(){
  document.getElementById("audioPlayer").currentTime = document.getElementById("startOffsetSelector").value;
}

let playing = false;
function playPause(){
  if(!playing){
    updateAudioPosition();
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


let bps = 64; // 64 pixels per second (1 block per pixel)
function renderCanvas(){
  if(!ctx){
    return;
  }
  const height = document.getElementById("canvas").height;
  const width = document.getElementById("canvas").width;

  ctx.clearRect(0, 0, width, height); // clear canvas


  let audioPosition = document.getElementById("audioPlayer").currentTime;
  let offset = audioPosition * bps;


  // draw gridlines for reference
  // this code doesn't really make much sense but it works
  ctx.fillStyle = "#ffffff";
  ctx.globalAlpha = 0.2;
  let bpg = 16; // 16 blocks per gridline
  let gridlineOffset = (audioPosition * bps) - (width / 4) % bpg;

  for(i = -gridlineOffset; i < width; i += (bpg)){
    ctx.fillRect(i, 0, 1, height);
  }

  // draw beats
  ctx.fillStyle = "#ff33e0";

  beats.forEach(b => {
    let startHeight = 0;
    let endHeight = height;
    switch(b.side){
      
      case "l":
        startHeight = 0;
        endHeight = height / 2;
        break;
      case "r":
        startHeight = height / 2;
        endHeight = height;
        break;
    }

    ctx.globalAlpha = b.height / 3;

    ctx.fillRect(b.time * bps - offset + width / 4, startHeight, 1, endHeight - startHeight);
  });

  ctx.globalAlpha = 1.0;

  // draw horizontal line across centre
  ctx.fillStyle = "#42f548";
  ctx.fillRect(0, (height / 2), width, 1);

  ctx.globalAlpha = 0.5;
  // draw vertical line down centre
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(width / 4, 0, 1, height);

}

function renderLoop(){
  setTimeout(() => {
    renderCanvas();
    renderLoop();
  }, 10);
}

renderLoop();

let beats = [];

document.addEventListener("keydown", (e) => {
  let side = "";
  switch(e.key){
    case "ArrowLeft":
      side = "l";
      break;
    case "ArrowRight":
      side = "r";
      break;
    case "ArrowUp":
      side = "b";
      break;
    default:
      return;
  }

  e.preventDefault();

  let x = Math.round(document.getElementById("audioPlayer").currentTime * bps);
  let time = x / bps;

  beats.push({
    "time": time,
    "x": x,
    "height": document.querySelector('input[name="level"]:checked').value,
    "side": side
  })
})

function exportFile(){
  download("torches.json", JSON.stringify(beats));
}

// https://stackoverflow.com/a/18197341
function download(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}