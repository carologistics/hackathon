import cv2
import numpy as np
import time 
from ultralytics import # Your code here


# CONSTANTS
MODEL_PATH = None # Your code here
VIDEO_PATH = "task1/box_front.mp4"
TARGET_SIZE = 640
IOU_THRESHOLD = 0.5
OUTPUT_FILE_NAME = "task1/output_" + MODEL_PATH + ".mp4"

def load_model(path): # Your code here
    pass


# RESIZE
def resize_with_aspect_ratio(frame, target):
    h, w = frame.shape[:2]
    scale = target / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(frame, (new_w, new_h))


# IOU
def compute_iou(mask1, mask2):
    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()
    return intersection / union if union > 0 else 0


# MASK PROCESSING
def prepare_mask(mask, frame_shape):
    if mask.shape != frame_shape[:2]:
        mask = cv2.resize(
        mask.astype(np.uint8),
        (frame_shape[1], frame_shape[0]),
        interpolation=cv2.INTER_NEAREST,
        )

    return mask.astype(bool)


# TRACKING (COLOR MATCHING)
def match_mask_to_previous(mask, prev_masks, prev_colors):
    best_iou = 0
    best_idx = -1
    for i, prev_mask in enumerate(prev_masks):
        iou = compute_iou(mask, prev_mask)
        if iou > best_iou:
            best_iou = iou
            best_idx = i
    if best_iou > IOU_THRESHOLD:
        return prev_colors[best_idx]  
    else:
        return np.random.randint(100, 256, size=3)


# DRAWING
def apply_mask_overlay(frame, masks, prev_masks, prev_colors):
    overlay = frame.copy()
    current_colors = []
    processed_masks = []
    for mask in masks:
        mask = prepare_mask(mask, frame.shape)
        processed_masks.append(mask)
        color = match_mask_to_previous(mask, prev_masks, prev_colors)
        current_colors.append(color)
        overlay[mask] = (0.5 * overlay[mask] + 0.5 * color).astype(np.uint8)
    return overlay, processed_masks, current_colors


# MAIN LOOP
def process_video():
    model = load_model(MODEL_PATH) 
    cap = cv2.VideoCapture(VIDEO_PATH)
    prev_masks = []
    prev_colors = []
    inference_times = []
    out = None
    while True:
        ret, frame = cap.read()
        # video end
        if not ret:
            break
        # standardize the input size
        frame = resize_with_aspect_ratio(frame, TARGET_SIZE)
        # initialize writer once we know frame size
        if out is None:
            h, w = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(OUTPUT_FILE_NAME, fourcc, 30, (w, h))
        start_time = time.perf_counter()
        results = model(frame)
        end_time = time.perf_counter()
        inference_time = end_time - start_time
        inference_times.append(inference_time)
        if results[0].masks is not None:
            masks = results[0].masks.data.cpu().numpy()
            frame, prev_masks, prev_colors = apply_mask_overlay(
            frame, masks, prev_masks, prev_colors
        )
        out.write(frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    avg_time = sum(inference_times) / len(inference_times)
    print(f"Average inference time: {avg_time:.4f} seconds")
    cap.release()
    out.release()


# ENTRY POINT
if __name__ == "__main__":
    process_video()
