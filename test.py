import cv2
import json
import base64
import numpy as np
import requests
import time
from collections import deque

def api_preprocess(frame):
    encoded = base64.b64encode(cv2.imencode('.jpg', frame)[1])
    return encoded

frame_idx = 0
previous_frames = []
latest_results = None
inference_tock = 0
cum_inference_tock = 0.0

fourcc = cv2.VideoWriter_fourcc(*'mp4V')
out = cv2.VideoWriter('server_output.mp4', fourcc, 24, (1280, 720))

def accumulate_global_output_frames():
	global previous_frames, frame_idx, polling_rate, global_output_frames, boxes, latest_results, inference_tock

	while True:
		has_frame, frame = cap.read()

		if has_frame:
			frame = cv2.resize(frame, (736, 736)) # do not remove this line
			# frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			# frame = np.stack([frame, frame, frame], axis = 2)
			# print(frame.shape)
			
			inference_tick = time.time()
			encoded_frame = api_preprocess(frame)
			response = requests.post(
				'http://127.0.0.1:9095/inference/',
				{
					'file': encoded_frame,
					'frame_idx': str(frame_idx),
					'imgsz': 736,
					'conf': 0.3,
					'iou': 0.4,
					'sampling_step': 5,
				}
			)
			inference_tock = time.time() - inference_tick

			if response.status_code == 200:
				interpolated_boxes = json.loads(response.text)
				if interpolated_boxes is not None:
					if len(interpolated_boxes):
						global_output_frames.append((frame, interpolated_boxes))
					else:
						global_output_frames.append((frame, []))
				else:
					global_output_frames.append((frame, []))

			frame_idx += 1

		else:
			cap.release()
			break
	

def visualize_live_playback():
	global global_output_frames, fps, cum_inference_tock
	frame_index_20 = 0
	tic_20 = None

	tic_cum = None
	frame_index_cum = 0
	
	fps_20 = None

	while True:
		if len(global_output_frames):
			if frame_index_20 % 20 == 0:
				tic_20 = time.time()
				frame_index_20 = 0

			if tic_cum is None:
				tic_cum = time.time()

			frame_index_20 += 1
			frame_index_cum += 1
			output_frame, boxes = global_output_frames.popleft()

			for box in boxes:
				top_left, bottom_right = box
				cv2.rectangle(output_frame, top_left, bottom_right, [0, 0, 255], 2)
				
				# cv2.putText(
				# 	img = output_frame,
				# 	text = f'{class_idx}',
				# 	org = (top_left[0], top_left[1] - 5),
				# 	fontScale = 0.5,
				# 	fontFace = 0,
				# 	color = [255, 0, 0],
				# 	thickness = 2,
				# )

			# for box in last_boxes:
			# 	top_left, bottom_right = box
			# 	cv2.rectangle(output_frame, top_left, bottom_right, [255, 0, 0], 2)

			# if frame_index_20 == 20:
			# 	fps_20 = f'Avg Playback Fps({((frame_index_20) / (time.time() - tic_20 + 1e-8)):.3f})'

			# cv2.putText(
			# 	img = output_frame,
			# 	text = fps_20,
			# 	org = (10, 40),
			# 	fontScale = 1,
			# 	fontFace = 0,
			# 	color = [0, 200, 0],
			# 	thickness = 4,
			# )

			# cv2.putText(
			# 	img = output_frame,
			# 	text = f'Current Playback Fps({((frame_index_cum) / (time.time() - tic_cum + 1e-8)):.3f})',
			# 	org = (10, 85),
			# 	fontScale = 1,
			# 	fontFace = 0,
			# 	color = [0, 200, 0],
			# 	thickness = 4,
			# )
			# cum_inference_tock = 0.8 * cum_inference_tock + 0.2 * inference_tock

			# cv2.putText(
			# 	img = output_frame,
			# 	text = f'Inference Fps({1 / cum_inference_tock:.3f})',
			# 	org = (10, 125),
			# 	fontScale = 1,
			# 	fontFace = 0,
			# 	color = [0, 200, 0],
			# 	thickness = 4,
			# )

			output_frame = cv2.resize(output_frame, (1280, 720))
			cv2.imshow("Outputs", output_frame)
			out.write(output_frame)
		
		if frame_index_cum > 1000:
			out.release()
			print('Output video is completed!')
			break

		cv2.waitKey(30)

if __name__ == '__main__':
	from threading import Thread

	cap = cv2.VideoCapture('assets/videos/video1.mp4')
	fps = int(cap.get(cv2.CAP_PROP_FPS))

	frame_idx = 0
	sampling_fps = 5
	polling_rate = int(fps / sampling_fps)
	global_output_frames = deque()

	try:
		t1 = Thread(target = accumulate_global_output_frames)
		t2 = Thread(target = visualize_live_playback)
		
		t1.start()
		t2.start()

		t1.join()
		t2.join()
	except KeyboardInterrupt:
		exit(0)