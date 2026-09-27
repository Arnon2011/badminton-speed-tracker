import streamlit as st
import cv2
import numpy as np

st.title("🏸 Badminton Speed Tracker")

# Step 1: Upload Video
uploaded_file = st.file_uploader("Upload smash video", type=["mp4", "avi"])

if uploaded_file:
    # Save temporarily
    with open("temp.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    # Step 2: Show First Frame for Calibration
    cap = cv2.VideoCapture("temp.mp4")
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        st.write("### 🔧 Calibrate Your Camera")
        st.write("Click TWO points on a known distance (e.g., 1-meter mark on floor):")
        
        # Use st.image with click detection (Streamlit doesn't natively support mouse clicks on images easily)
        # WORKAROUND: Let users enter pixel coordinates manually OR use a library like 'streamlit-drawable-canvas'
        from streamlit_drawable_canvas import st_canvas
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#ffa500",
            background_image=frame,
            update_streamlit=True,
            height=400,
            drawing_mode="point",  # Allows clicking points
            key="canvas"
        )
        
        # Extract clicked points
        if canvas_result.json_data is not None:
            objects = pd.json_normalize(canvas_result.json_data["objects"])
            if len(objects) >= 2:
                p1 = (objects.iloc[0]["left"], objects.iloc[0]["top"])
                p2 = (objects.iloc[1]["left"], objects.iloc[1]["top"])
                dist_px = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                
                known_dist_m = st.number_input("Known distance (meters)", value=1.0, step=0.1)
                pixels_per_meter = dist_px / known_dist_m
                
                st.success(f"✅ Calibration: {pixels_per_meter:.1f} px/m")