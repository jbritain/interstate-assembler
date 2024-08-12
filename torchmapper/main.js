let canvas;
let gapThreshold = 4;

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
  canvas = document.getElementById("canvas");
  ctx = canvas.getContext("2d");
  fixDpi();
  renderCanvas();
}

// https://medium.com/wdstack/fixing-html5-2d-canvas-blur-8ebe27db07da
function fixDpi() {
  const dpr = window.devicePixelRatio;
  const rect =  canvas.getBoundingClientRect();
  ctx.scale(dpr, dpr);
  canvas.style.width = `${rect.width}px`;
  canvas.style.height = `${rect.height}px`;
  canvas.width = `${rect.width}`;
  canvas.height = `${rect.width}`;
}

// https://github.com/gre/smoothstep/blob/master/index.js
function smoothstep (min, max, value) {
  var x = Math.max(0, Math.min(1, (value-min)/(max-min)));
  return x;
};

function getBeatColour(b){
  switch(b.height){
    case "1":
      return "red";
    case "2":
      return "yellow";
    case "3":
      return "blue";
  }
}

let bps = 64; // 64 pixels per second (1 block per pixel)
function renderCanvas(){
  if(!ctx){
    return;
  }
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  const height = canvas.height;
  const width = canvas.width;

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
  ctx.globalAlpha = 1.0;

  let lastBeatHit; // the last beat we have already passed
  beats.forEach(b => {
    const beatPlayed = b.time * bps - offset < 0;
    let beatNewer = true;
    if(typeof lastBeatHit != "undefined"){
      beatNewer = lastBeatHit.time < b.time;
    }

    if(beatPlayed && beatNewer){
      lastBeatHit = b;
    }

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

    ctx.fillStyle = getBeatColour(b);

    ctx.fillRect(b.time * bps - offset + width / 4, startHeight, 1, endHeight - startHeight);
  });

  if(typeof(lastBeatHit) != "undefined"){
    document.getElementById("pulser").style.backgroundColor = getBeatColour(lastBeatHit);
    document.getElementById("pulser").style.borderColor = getBeatColour(lastBeatHit);
    document.getElementById("pulser").style.opacity = smoothstep(-0.5 * bps, 0, lastBeatHit.time * bps - offset);

  } else {
    document.getElementById("pulser").style.backgroundColor = "";
  }
  
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
  renderCanvas();
  requestAnimationFrame(renderLoop);
}

renderLoop();

let beats = [];

document.addEventListener("keydown", (e) => {
  let side = "";
  let height = "";
  switch(e.code){
    case "Numpad7":
      side = "l";
      height = "3";
      break;
    case "Numpad8":
      side = "b";
      height = "3";
      break;
    case "Numpad9":
      side = "r";
      height = "3";
      break;
    case "Numpad4":
      side = "l";
      height = "2";
      break;
    case "Numpad5":
      side = "b";
      height = "2";
      break;
    case "Numpad6":
      side = "r";
      height = "2";
      break;
    case "Numpad1":
      side = "l";
      height = "1";
      break;
    case "Numpad2":
      side = "b";
      height = "1";
      break;
    case "Numpad3":
      side = "r";
      height = "1";
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
    "height": height,
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

function importJson(){
  try {
    beats = beats.concat(JSON.parse(window.prompt("Paste JSON String")));
  } catch(e) {
    window.Error("Invalid json!");
  }
  
}

function fixGaps(){
  beats.sort((a,b) => a.x - b.x);
  let lastBeat = beats[0];
  beats.forEach(beat => {
    if(Math.abs(lastBeat.x - beat.x) <= gapThreshold){
      beat.x = lastBeat.x;
      beat.time = lastBeat.time;
    }
    lastBeat = beat;
  })
}

function undo(){
  beats.pop();
}