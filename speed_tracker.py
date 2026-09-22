import cv2
import numpy as np
import time

# Force Mac-native camera backend
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

if not cap.isOpened():
    print("❌ Camera failed to open.")
    exit()

print("✅ Camera connected!")

# Get frame size
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 30.0
print(f"📹 Resolution: {width}x{height} @ {fps} FPS")

# Setup video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('badminton_smash.mp4', fourcc, fps, (width, height))

# CALIBRATION: Measure a known distance in your video (in pixels)
# Example: If a 1-meter ruler appears as 200 pixels wide in your frame
PIXELS_PER_METER = 200  # ← YOU MUST MEASURE THIS FOR YOUR SETUP!

print("🎥 Recording started... Press 'q' to stop.")
print("⚠️  Make sure background is plain and lighting is good!")

last_pos = None
last_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define range for WHITE shuttlecock in HSV
    # White has low saturation and high value
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Clean up the mask
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours (shapes) in the white mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_pos = None
    if contours:
        # Get the largest contour (most likely the shuttlecock)
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        # Filter out noise (too small or too large)
        if 50 < area < 5000:
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                current_pos = (cx, cy)

                # Draw circle around detected shuttlecock
                cv2.circle(frame, (cx, cy), 15, (0, 255, 0), -1)

    # Calculate speed if we have two positions
    speed_text = "Speed: -- km/h"
    if current_pos and last_pos:
        current_time = time.time()
        time_diff = current_time - last_time

        if time_diff > 0:
            # Distance in pixels
            dist_px = np.sqrt((current_pos[0] - last_pos[0])**2 +
                              (current_pos[1] - last_pos[1])**2)

            # Convert to meters
            dist_m = dist_px / PIXELS_PER_METER

            # Speed in m/s then km/h
            speed_ms = dist_m / time_diff
            speed_kmh = speed_ms * 3.6

            speed_text = f"Speed: {speed_kmh:.1f} km/h"

        last_pos = current_pos
        last_time = current_time

    # Display speed on screen
    cv2.putText(frame, speed_text, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    # Write frame and show preview
    out.write(frame)
    cv2.imshow('Badminton Speed Tracker', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
out.release()
cv2.destroyAllWindows()
print("✅ Video saved! Check 'badminton_smash.mp4'")