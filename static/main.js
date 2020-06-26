var buttonRecord = document.getElementById("record");
var buttonStop = document.getElementById("recordStop");
var buttonStreamStop = document.getElementById("streamStop");
var buttonStreamPlay = document.getElementById("streamPlay");
var buttonTop = document.getElementById("topView");
var buttonCamera = document.getElementById("cameraView");
var noFeed=document.getElementById('noFeed');
var mainScreen = document.getElementById("mainFeed");

buttonStop.disabled = true;
buttonStreamPlay.disabled = true;
noFeed.hidden=true;

buttonCamera.onclick = function () {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/change-view");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ action: "Camera_View" }));
};

buttonTop.onclick = function () {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/change-view");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ action: "Top_View" }));
};

//show the main screen
buttonStreamPlay.onclick = function () {
  buttonStreamPlay.disabled = true;
  buttonStreamStop.disabled = false;

  mainScreen.hidden = false;
  noFeed.hidden=true;

};

//hide the main screen
buttonStreamStop.onclick = function () {
  buttonStreamStop.disabled = true;
  buttonStreamPlay.disabled = false;

  mainScreen.hidden = true;
  noFeed.hidden=false;
};

buttonRecord.onclick = function () {
  buttonRecord.disabled = true;
  buttonStop.disabled = false;

  // disable download link
  var downloadLink = document.getElementById("download");
  downloadLink.text = "";
  downloadLink.href = "";

  // XMLHttpRequest
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/record_status");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ status: "true" }));
};

buttonStop.onclick = function () {
  buttonRecord.disabled = false;
  buttonStop.disabled = true;

  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // enable download link
      var downloadLink = document.getElementById("download");
      downloadLink.text = "Download";
      downloadLink.href = "/static/video.avi";
    }
  };
  xhr.open("POST", "/record_status");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ status: "false" }));
};
