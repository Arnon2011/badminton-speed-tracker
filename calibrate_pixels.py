import cv2

# Load your test video frame (save a single frame as 'test_frame.jpg' first)
img = cv2.imread('test_frame.jpg')

# Set up mouse callback to click two points
points = []
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Clicked at: ({x}, {y})")
        if len(points) == 2:
            dist = abs(points[1][0] - points[0][0])
            print(f"✅ PIXELS_PER_METER = {dist}")
            cv2.destroyAllWindows()

cv2.imshow('Measure 1 Meter', img)
cv2.setMouseCallback('Measure 1 Meter', click_event)
cv2.waitKey(0)