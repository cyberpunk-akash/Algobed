#this code detects movement of the bot

from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2


#parsing arguments 
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
 
if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)
 

#making sure the initial frame is the still frame which acts as the background
#to the moving bot 

firstFrame = None

# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	text = "No movement"
 
 
	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	
	#purpose of grayscaling and blurring is for a clearer diffrentiation of the moving bot 
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
 
	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray
		continue
	
	# compute the absolute difference between the current frame and
	# first frame
	#frameDelta takes care of the difference between the moving bot and background by seeing 
	#for any change in the frame
	#frameDelta = cv2.absdiff(firstFrame, gray)
	
	#thresholding with a max value of 255 here means pixel intensity values less than 
	#25 get mapped to zero(black) and above 25 get mapped to 255(white) 
	thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)[1]
 
	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	
	#cnts is a numpy array that stores the values of the contours
	#contours are points with the same intensity or color
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
 
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue
 
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
	
	
	# draw the text and timestamp on the frame
	cv2.putText(frame, "Bot Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
 
	# show the frame and record if the user presses a key
	cv2.imshow("frame", frame)
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame ", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break
 
# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()