var buttonCameraStart = document.getElementById("camera-start");
var buttonPoseStart = document.getElementById("pose-start");
var buttonPoseSubmit = document.getElementById("pose-confirm");
var buttonPoseEdit = document.getElementById("pose-edit");

var iconPoseTick = document.getElementById("pose-tick");
var iconCameraTick = document.getElementById("camera-tick");

var form = document.getElementById("form");
var formContainer = document.getElementById("form-container");

var noFeedPose=document.getElementById('noFeed-pose');
var noFeedCam=document.getElementById('noFeed-camera');
var feedPose = document.getElementById("feed-pose");
var feedCam = document.getElementById("feed-cam");
var poseTextNotDone=document.getElementById("poseNotDone");
var poseTextDone=document.getElementById("poseDone");


//hide the form elements and ticks that appear on completion
iconCameraTick.style.display = "none";
iconPoseTick.style.display = "none";
formContainer.hidden = true;
form.style.display = "none";
buttonPoseSubmit.hidden = true;
buttonPoseEdit.hidden = true;
noFeedPose.hidden=false;
noFeedCam.hidden=true;
feedPose.hidden=true;
feedCam.hidden=false;
poseTextDone.hidden=true;

//disable editing of form until edit button is pressed
form.elements[0].disabled = true;
form.elements[1].disabled = true;
form.elements[2].disabled = true;
form.elements[3].disabled = true;
form.elements[4].disabled = true;
form.elements[5].disabled = true;
form.elements[6].disabled = true;

//camera calibration start function
//send an http request to server to start the function
buttonCameraStart.onclick = function () {
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/change-view");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ action: "Start_Camera" }));

  iconCameraTick.style.display = "block";
  noFeedPose.hidden=true;
  feedPose.hidden=false;
  noFeedCam.hidden=false;
  feedCam.hidden=true;
  poseTextNotDone.hidden=true;
};

//for the pose calibration
buttonPoseStart.onclick = function () {
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/change-view");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({ action: "Start_Pose" }));
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      //show the received response in the form
      data = JSON.parse(xhr.response);
      form.elements[0].value = data["length"];
      form.elements[1].value = data["width"];
      form.elements[2].value = data["height"];
      form.elements[3].value = data["distance"];
      form.elements[4].value = data["yoke"];
      form.elements[5].value = data["pitch"];
      form.elements[6].value = data["roll"];

      //make the form visible on clicking button
      formContainer.hidden=false;
      iconPoseTick.style.display = "block";
      form.style.display = "flex";
      feedPose.hidden=true;
      noFeedPose.hidden=false;
      poseTextDone.hidden=false;
      buttonPoseEdit.hidden=false;
      buttonPoseSubmit.hidden=false
    }
  };
};

//submit the form details to save it in a yaml file
buttonPoseSubmit.onclick = function () {
  var data = {
    length: form.elements[0].value,
    width: form.elements[1].value,
    height: form.elements[2].value,
    distance: form.elements[3].value,
    yoke: form.elements[4].value,
    pitch: form.elements[5].value,
    roll: form.elements[6].value,
  };

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/save-changes");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify(data));
};

//just activate the form elements for editing
buttonPoseEdit.onclick = function () {
  form.elements[0].disabled = false;
  form.elements[1].disabled = false;
  form.elements[2].disabled = false;
  form.elements[3].disabled = false;
  form.elements[4].disabled = false;
  form.elements[5].disabled = false;
  form.elements[6].disabled = false;
};
