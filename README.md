# SocialDistancingUI
UI for the Social Distancing Surveilance system developed by AGV, IIT Kharagpur

## Dependencies
- Flask
- PyYaml
- Opencv

## How To Run
- Install Flask
```
pip install flask
```
- Install PyYaml
```
pip install pyyaml
```
- To start the main program run
```
python3 main.py
```
## File Structure
- **main.py** is the main server file
- **camera.py** is the Camera object
- **RecoverPose.py** is for the Recalibration
- **cameraCalib.py** is for the Camera Calibration
- **data.yaml** file is where the calibration ouput is saved
- **min_dist.txt** file is where the minimum physical distance threshold is set
- **Templates folder** contains the html files
- **Static folder** contains the js and css files
- __pycache__ is the automatically generated cache file
