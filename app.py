import streamlit as st
import cv2
import numpy as np
import time

# --- CONFIGURATION ---
# You must update this after calibrating at the court!
PIXELS_PER_METER = 200 

st.title("🏸 Badminton Speed Tracker")
st.write("Upload a video of a badminton smash to analyze the speed.")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])

if uploaded_file:
    # Save uploaded file temporarily
    tfile = open("temp_video.mp4", "wb")
    tfile.write(uploaded_file.read())
    tfile.close()
    
    st.video("temp_video.mp4")
    
    # --- PROCESSING ---
    cap = cv2.VideoCapture("temp_video.mp4")
    
    max_speed = 0
    last_pos = None
    last_time = time.time()
    
    # Progress bar for user feedback
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    my_bar = st.progress(0)
    status_text = st.empty()
    
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # ==========================================
        # PASTE YOUR SPEED DETECTION LOGIC HERE
        # (From your speed_tracker.py while loop)
        # ==========================================
        
        # Example placeholder logic:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        current_pos = None
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            if 50 < area < 5000:
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    current_pos = (cx, cy)
        
        # Calculate speed
        speed = 0
        if current_pos and last_pos:
            current_time = time.time()
            time_diff = current_time - last_time
            if time_diff > 0:
                dist_px = np.sqrt((current_pos[0] - last_pos[0])**2 + (current_pos[1] - last_pos[1])**2)
                dist_m = dist_px / PIXELS_PER_METER
                speed_ms = dist_m / time_diff
                speed = speed_ms * 3.6
                
            last_pos = current_pos
            last_time = current_time
            
        # ==========================================
        # END OF SPEED DETECTION LOGIC
        # ==========================================

        if speed > max_speed:
            max_speed = speed
            
        frame_count += 1
        my_bar.progress(frame_count / total_frames)
        status_text.text(f"Processing frame {frame_count}/{total_frames}... Current Speed: {speed:.1f} km/h")

    cap.release()
    
    # --- RESULTS ---
    st.success("Analysis Complete!")
    st.metric("Max Smash Speed", f"{max_speed:.1f} km/h")