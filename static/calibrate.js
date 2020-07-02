//get the required html DOM elements as objects
var buttonMarkerEdit = document.getElementById("marker-edit");
var buttonMarkerConfirm = document.getElementById("marker-confirm");
var buttonPoseSubmit = document.getElementById("pose-confirm");
var buttonPoseEdit = document.getElementById("pose-edit");
var buttonCalibStart = document.getElementById("start-calib");

var form = document.getElementById("form");
var formConatiner = document.getElementById("form-container");
var markerInput = document.getElementById("marker-input");

var noFeedCam = document.getElementById("noFeed-camera");
var feedCam = document.getElementById("feed-cam");

var iconCalibTick = document.getElementById("calib-tick");

//hide the tick till calibration is done
iconCalibTick.style.display = "none";

// disable editing of form until edit button is pressed
form.elements[0].disabled = true;
form.elements[1].disabled = true;
form.elements[2].disabled = true;
form.elements[3].disabled = true;
form.elements[4].disabled = true;

markerInput.disabled = true;
//default dimensions of marker
markerInput.value = "7.2";

//enable editing on marker dimensions
buttonMarkerEdit.onclick = function () {
  markerInput.disabled = false;
};

//send the updatated data to the server
buttonMarkerConfirm.onclick = function () {
  markerInput.disabled = true;
  var data = {
    "side-length": markerInput.value,
  };

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/marker-dimension");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify(data));
  
};

//enable editing in form
buttonPoseEdit.onclick = function () {
  form.elements[0].disabled = false;
  form.elements[1].disabled = false;
  form.elements[2].disabled = false;
  form.elements[3].disabled = false;
  form.elements[4].disabled = false;
};

//send data to server where it is saved as yaml file
buttonPoseSubmit.onclick = function () {
  var data = {
    height: form.elements[0].value,
    distance: form.elements[1].value,
    yaw: form.elements[2].value,
    pitch: form.elements[3].value,
    roll: form.elements[4].value,
  };

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/save-changes");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify(data));
};

//send start calibration command to server
//the data received in shown on the form
buttonCalibStart.onclick = function () {
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/calib-start");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ action: "Start_Pose" }));
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      //show the received response in the form
      data = JSON.parse(xhr.response);
      form.elements[0].value = data["height"];
      form.elements[1].value = data["distance"];
      form.elements[2].value = data["yaw"];
      form.elements[3].value = data["pitch"];
      form.elements[4].value = data["roll"];

      //make the tick visible after finishing
      iconCalibTick.style.display = "block";
    }
  };
};
