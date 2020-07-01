//get the required html DOM elements as objects
var buttonStreamStop = document.getElementById("streamStop");
var buttonStreamPlay = document.getElementById("streamPlay");
var buttonEditThresh = document.getElementById("thresh");
var buttonReCalib = document.getElementById("recalib");

var noFeed = document.getElementById("noFeed");
var mainScreen = document.getElementById("mainFeed");

var toggleAuto = document.getElementById("toggle-auto");

var minDistForm = document.getElementById("min-dist");

//disable editing in the min-distance threshold input
minDistForm.elements[0].disabled = true;
//default min physical distance in meter
minDistForm.elements[0].value = "1";

//streaming controls
buttonStreamPlay.disabled = true;
noFeed.hidden = true;

//variable to check whether auto recalibration is on or off
var is_auto = toggleAuto.checked;

//switch to toggle is_auto
toggleAuto.onchange = function () {
  
  is_auto = !is_auto;
  //send the server information about the change
  if (is_auto) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/recalib");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ action: "auto-calib" }));
  } else {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/recalib");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ action: "manual-calib" }));
  }
};

//ask the server to recalibrate the system now
buttonReCalib.onclick = function () {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/recalib");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ action: "calib-now" }));
};


//show the streaming
buttonStreamPlay.onclick = function () {
  buttonStreamPlay.disabled = true;
  buttonStreamStop.disabled = false;

  mainScreen.hidden = false;
  noFeed.hidden = true;
};

//hide the streaming
buttonStreamStop.onclick = function () {
  buttonStreamStop.disabled = true;
  buttonStreamPlay.disabled = false;

  mainScreen.hidden = true;
  noFeed.hidden = false;
};

//set the minimum threshold distance
buttonEditThresh.onclick = function () {
  if (buttonEditThresh.textContent == "Edit") {
    minDistForm.elements[0].disabled = false;
    buttonEditThresh.textContent = "Confirm";
  } else {
    //when confirmed send the server the required information
    minDistForm.elements[0].disabled = true;
    buttonEditThresh.textContent = "Edit";

    var data = {
      "min-dist": minDistForm.elements[0].value,
    };  

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/min-dist");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(data));
  }
};
