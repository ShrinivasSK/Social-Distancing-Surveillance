//get the required html DOM elements as objects
var buttonStreamStop = document.getElementById("streamStop");
var buttonStreamPlay = document.getElementById("streamPlay");
var buttonEditThresh = document.getElementById("thresh");
var buttonReCalib = document.getElementById("recalib");

var containerCalib = document.getElementById("container-recab");
var containerControl = document.getElementById("container-control");
var containerDist = document.getElementById("container-dist");

var iconCalib = document.getElementById("down-recab");
var iconControl = document.getElementById("down-control");
var iconDist = document.getElementById("down-dist");

var noFeed = document.getElementById("noFeed");
var mainScreen = document.getElementById("mainFeed");

var toggleAuto = document.getElementById("toggle-auto");

var minDistForm = document.getElementById("min-dist");

var loginForm = document.getElementById("login-form");
var buttonLogin = document.getElementById("button-login");
var backdrop = document.getElementById("backdrop");
var box = document.getElementById("box");
var errorOutput = document.getElementById("submission-output");

globalusername = "admin";
globalpassword = "admin";
minDistThresh = "2";

buttonLogin.onclick = function () {
  var username = loginForm.elements[0].value;
  var password = loginForm.elements[1].value;
  if (username != globalusername) {
    errorOutput.innerHTML = "Enter correct username";
  } else if (password != globalpassword) {
    errorOutput.innerHTML = "Enter correct password";
  } else {
    backdrop.style.display = "none";
    box.style.display = "none";
    mainScreen.hidden = false;
    noFeed.hidden = true;
  }
};

//disable editing in the min-distance threshold input
minDistForm.elements[0].disabled = true;
//default min physical distance in meter
minDistForm.elements[0].value = minDistThresh;

//streaming controls
buttonStreamPlay.disabled = true;
mainScreen.hidden = true;
noFeed.hidden = false;

//variable to check whether auto recalibration is on or off
toggleAuto.checked = true;
var is_auto = toggleAuto.checked;

var body = document.getElementById("body");

body.onload = function () {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/start_stop_index");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ action: "start" }));
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      //show the received response in the form
      data = JSON.parse(xhr.response);
      globalpassword = data["username"];
      globalusername = data["password"];
      minDistThresh = data["thresh"];
      minDistForm.elements[0].value = minDistThresh / 100;
    }
  };
};

$(window).bind("beforeunload", function () {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/start_stop_index");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ action: "stop" }));
});
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

//For mobile view
iconCalib.onclick = function () {
  if (iconCalib.innerHTML == "arrow_drop_down") {
    containerCalib.style.display = "flex";
    iconCalib.innerHTML = "arrow_drop_up";
  } else {
    containerCalib.style.display = "none";
    iconCalib.innerHTML = "arrow_drop_down";
  }
};

iconControl.onclick = function () {
  if (iconControl.innerHTML == "arrow_drop_down") {
    containerControl.style.display = "flex";
    iconControl.innerHTML = "arrow_drop_up";
  } else {
    containerControl.style.display = "none";
    iconControl.innerHTML = "arrow_drop_down";
  }
};

iconDist.onclick = function () {
  if (iconDist.innerHTML == "arrow_drop_down") {
    containerDist.style.display = "flex";
    iconDist.innerHTML = "arrow_drop_up";
  } else {
    containerDist.style.display = "none";
    iconDist.innerHTML = "arrow_drop_down";
  }
};
