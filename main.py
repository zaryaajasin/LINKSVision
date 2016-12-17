import cv2
import numpy as np



largestArea = 0
cx, cy = 0, 0


#DEBUG Variables
debug = True #Do we want to see an image output?
networkTables = True #Are we testing out the Network Tables?


filterArea = 1000

#Set up NetworkTables




cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_EXPOSURE, 1)

while True:
    #reads in the video and breaks it into frames
    running, frame            = cap.read()

    if running:
        #First, we need to blur the image so contours are nicer
        frame = cv2.GaussianBlur(frame, (5,5), 0)
        
        #So, next we need to convert the frame to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #The Ranges of Green Color
        lower_green = np.array([80,100,100])
        upper_green = np.array([100,255,255])

        #Now, we need to find out what is in that range
        #OpenCV will return a binary image where white = 1
        #and black = 0
        mask = cv2.inRange(hsv, lower_green, upper_green)

        #The Kernel is just an array that is scanned over the
        #image. It is full of ones so it doesn't change anything.
        kernel = np.ones((5,5), np.uint8)

        #Now, we need to remove more noise! This can be done
        #with erosion. When we erode, the program looks to see
        #if a zero is in the neighborhood of its scan. If it is,
        #the range of that kernel is 0.
        mask = cv2.erode(mask, kernel, iterations = 1)
        mask = cv2.dilate(mask, kernel, iterations = 1)

        if debug:
            #This produces an image that is a combination
            #of the mask and original frame
            res = cv2.bitwise_and(hsv, frame, mask = mask)

        #Now, let's find some contours!
        _, contours, _ = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        #Needed otherwise the program will crash
        if len(contours) >= 1:
            largestArea = 0
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area >= largestArea * .8 and area >= filterArea:
                    largestArea = area
                    M = cv2.moments(cnt)
                    #Also needed unless you like errors
                    if M["m00"] != 0:
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                        print("Center X: %s" %(cx))
                        print("Center Y: %s" %(cy))
                    else:
                        cx, cy = 0, 0                      

                    if debug:
                        #For visualization, it would be nice to see what the robot
                        #considers the largest rectangle to be. Time to introduce
                        #hulls & boxes!
            
                        #First, we tell the robot to look for the convex points around
                        #the contour.
                        hull = cv2.convexHull(cnt)
                        #With these points, we now are looking for the smallest
                        #rectangle around said points
                        rect = cv2.minAreaRect(hull)
                        #Unfortantly, minAreaRect() only gets the center (x,y),
                        #(width, height), angle of rotation. To get
                        #around this, we use the boxpoints function to get the
                        #corners of the rectangle.
                        box = cv2.boxPoints(rect)
                        #With the corners, now we 
                        box = np.int0(box)

                        #The Circle will be used as a reference of what
                        #the contour's center is
                        cv2.circle(res,(cx, cy), 8, (0,0,255), -1)
                        
                        
                    
        if debug:
            cv2.drawContours(res, contours, -1, (0, 255, 0), 3)
            cv2.circle(res,(cx, cy), 8, (0,0,255), -1)
            cv2.imshow("Initial", frame)
            cv2.imshow("Final", res)
            
    else:
        print("ERROR")

    if cv2.waitKey(5) == ord("q"): break
cv2.destroyAllWindows()
