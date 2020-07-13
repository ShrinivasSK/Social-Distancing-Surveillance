import os
import json
import cv2
import numpy as np
import pandas as pd

DETECTION_MODEL = 'ssd_mobilenet/'
SWAPRB = True

with open(os.path.join('models', DETECTION_MODEL, 'labels.json')) as json_data:
	CLASS_NAMES = json.load(json_data)


class Detector():
	"""Class ssd"""

	def __init__(self):
		self.model = cv2.dnn.readNetFromTensorflow(
			'models/ssd_mobilenet/frozen_inference_graph.pb',
			'models/ssd_mobilenet/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')

	def prediction(self, image):
		self.model.setInput(
			cv2.dnn.blobFromImage(image, size=(300, 300), swapRB=SWAPRB))
		output = self.model.forward()
		result = output[0, 0, :, :]
		return result

	def filter_prediction(self, output, image, conf_th=0.5, conf_class=[]):

		height, width = image.shape[:-1]
		df = pd.DataFrame(
			output,
			columns=[
				'_', 'class_id', 'confidence', 'x1', 'y1', 'x2', 'y2'])
		#nan_data=[col for col in df.columns if len(df[col].isnull())]
		#print(nan_data)
		df = df.fillna(110)
		nan_data=[col for col in df.columns if len(df[col].isnull())]
		try:

			df = df.assign(
				x1=lambda x: (x['x1'] * width).astype(int).clip(0),
				y1=lambda x: (x['y1'] * height).astype(int).clip(0),
				x2=lambda x: (x['x2'] * width).astype(int),
				y2=lambda x: (x['y2'] * height).astype(int),
				class_name=lambda x: (
					x['class_id'].astype(int).astype(str).replace(CLASS_NAMES)),)

			df['label'] = (df['class_name'] + ': ' +
					   df['confidence'].astype(str).str.slice(stop=4))
			df = df[df['confidence'] > conf_th]
			if len(conf_class) > 0:
				df = df[df['class_id'].isin(conf_class)]
			df = df[df['class_name'] == 'person']
			return df

		except:
			print("NAN value")

		

	def draw_boxes(self, image, df):
		for _, box in df.iterrows():
			x_min, y_min, x_max, y_max = box['x1'], box['y1'], box['x2'], box['y2']
			color = (0, 0, 0)
			cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), color, 2)
		return image

	def mid_point(self, image, df):
		p = []
		for _, box in df.iterrows():
			x_min, y_min, x_max, y_max = box['x1'], box['y1'], box['x2'], box['y2']
			p.append((int((x_min+x_max)/2), y_max))
		return p
