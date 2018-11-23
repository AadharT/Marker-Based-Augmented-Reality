

import numpy as np
import cv2
import cv2.aruco as aruco
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

import pygame


texture_object = None
texture_background = None
camera_matrix = None
dist_coeff = None
cap = cv2.VideoCapture(0)
INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [ 1.0, 1.0, 1.0, 1.0]])

################## Define Utility Functions Here #######################
"""
Function Name : getCameraMatrix()
Input: None
Output: camera_matrix, dist_coeff
Purpose: Loads the camera calibration file provided and returns the camera and
         distortion matrix saved in the calibration file.
"""
def getCameraMatrix():
        global camera_matrix, dist_coeff
        with np.load('System.npz') as X:
                camera_matrix, dist_coeff, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]



########################################################################

############# Main Function and Initialisations ########################
"""
Function Name : main()
Input: None
Output: None
Purpose: Initialises OpenGL window and callback functions. Then starts the event
         processing loop.
"""
def main():
        glutInit()
        getCameraMatrix()
        glutInitWindowSize(640, 480)
        glutInitWindowPosition(625, 100)
        glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
        window_id = glutCreateWindow("OpenGL")
        init_gl()
        glutDisplayFunc(drawGLScene)
        glutIdleFunc(drawGLScene)
        glutReshapeFunc(resize)
        glutMainLoop()

"""
Function Name : init_gl()
Input: None
Output: None
Purpose: Initialises various parameters related to OpenGL scene.
"""
def init_gl():
        global texture_object, texture_background
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        texture_background = glGenTextures(1)
        texture_object = glGenTextures(1)
"""
Function Name : resize()
Input: None
Output: None
Purpose: Initialises the projection matrix of OpenGL scene
"""
def resize(w,h):
        ratio = 1.0* w / h
        glMatrixMode(GL_PROJECTION)
        glViewport(0,0,w,h)
        gluPerspective(45, ratio, 0.1, 100.0)

"""
Function Name : drawGLScene()
Input: None
Output: None
Purpose: It is the main callback function which is called again and
         again by the event processing loop. In this loop, the webcam frame
         is received and set as background for OpenGL scene. ArUco marker is
         detected in the webcam frame and 3D model is overlayed on the marker
         by calling the overlay() function.
"""
def drawGLScene():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ar_list = []
        ret, frame = cap.read()
        if ret == True:
                #image_arr = array(frame)
                #draw_background(frame)

                glutPostRedisplay()
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                ar_list = detect_markers(frame)
                for i in ar_list:
##                        if i[0] == 8:
##                                overlay(frame, ar_list, i[0],"texture_1.png")
##                        if i[0] == 2:
##                                overlay(frame, ar_list, i[0],"texture_2.png")
##                        if i[0] == 7:
##                                overlay(frame, ar_list, i[0],"texture_3.png")
                    if i[0] == 2:
                        overlay(frame, ar_list, i[0],"texture_4.png")

                cv2.imshow('frame', frame)
                cv2.waitKey(1)
        glutSwapBuffers()

########################################################################

######################## Aruco Detection Function ######################
"""
Function Name : detect_markers()
Input: img (numpy array)
Output: aruco list in the form [(aruco_id_1, centre_1, rvec_1, tvec_1),(aruco_id_2,
        centre_2, rvec_2, tvec_2), ()....]
Purpose: This function takes the image in form of a numpy array, camera_matrix and
         distortion matrix as input and detects ArUco markers in the image. For each
         ArUco marker detected in image, paramters such as ID, centre coord, rvec
         and tvec are calculated and stored in a list in a prescribed format. The list
         is returned as output for the function
"""
def detect_markers(img):
        aruco_list=[]
        markerLength = 100
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_250)
        parameters = cv2.aruco.DetectorParameters_create()
        corners, ids, _ = cv2.aruco.detectMarkers(img,aruco_dict,parameters = parameters)
        rvect, tvect, _ = cv2.aruco.estimatePoseSingleMarkers(corners,100, camera_matrix, dist_coeff)
        if (ids):
            for x in range(len(ids)):
                aruco_id=ids[x][0]
                aruco_centre=(((corners[x][0][0][0]+corners[x][0][2][0])/2,(corners[x][0][0][1]+corners[x][0][2][1])/2))
                rvec,tvec=rvect[x][0],tvect[x][0]
                aruco_list.append([aruco_id,aruco_centre,rvec,tvec])
        else:
            print ("No Aruco Markers")
        #print(aruco_list)
        return aruco_list
"""
Function Name : draw_background()
Input: img (numpy array)
Output: None
Purpose: Takes image as input and converts it into an OpenGL texture. That
         OpenGL texture is then set as background of the OpenGL scene
"""
def draw_background(img):
        height, width = img.shape[:2]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.flip(img, 0, img)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindTexture(GL_TEXTURE_2D, texture_background)

        glTexImage2D(GL_TEXTURE_2D,
        0,
        GL_RGB,
        width,
        height,
        0,
        GL_RGB,
        GL_UNSIGNED_BYTE,
        img)
        glEnable(GL_TEXTURE_2D)
        #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        #this one is necessary with texture2d for some reason
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        # Set Projection Matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)

        # Switch to Model View Matrix
        # glMatrixMode(GL_MODELVIEW)
        # glLoadIdentity()

        # Draw textured Quads
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(width, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(width, height)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0.0, height)
        glEnd()


        glDisable(GL_TEXTURE_2D)

        return None

"""
Function Name : init_object_texture()
Input: Image file path
Output: None
Purpose: Takes the filepath of a texture file as input and converts it into OpenGL
         texture. The texture is then applied to the next object rendered in the OpenGL
         scene.
"""
def init_object_texture(image_filepath):
        tex = cv2.imread(image_filepath)
        height, width = tex.shape[:2]
        tex = cv2.cvtColor(tex, cv2.COLOR_BGR2RGB)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindTexture(GL_TEXTURE_2D, texture_object)

        glTexImage2D(GL_TEXTURE_2D,
        0,
        GL_RGB,
        width,
        height,
        0,
        GL_RGB,
        GL_UNSIGNED_BYTE,
        tex)
        glEnable(GL_TEXTURE_2D)
        #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        #this one is necessary with texture2d for some reason
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        # Set Projection Matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        return None

"""
Function Name : overlay()
Input: img (numpy array), aruco_list, aruco_id, texture_file (filepath of texture file)
Output: None
Purpose: Receives the ArUco information as input and overlays the 3D Model of a teapot
         on the ArUco marker. That ArUco information is used to
         calculate the rotation matrix and subsequently the view matrix. Then that view matrix
         is loaded as current matrix and the 3D model is rendered.

         Parts of this code are already completed, you just need to fill in the blanks. You may
         however add your own code in this function.
"""
def overlay(img, ar_list, ar_id, texture_file):
        for x in ar_list:
                if ar_id == x[0]:
                        centre, rvec, tvec = x[1], x[2], x[3]
        rmtx = cv2.Rodrigues(rvec)[0]
        print tvec
        #glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvec[0]],
                        [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvec[1]],
                        [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvec[2]],
                        [0.0       ,0.0       ,0.0       ,1.0    ]])
        view_matrix = view_matrix * INVERSE_MATRIX
        view_matrix = np.transpose(view_matrix)


        #init_object_texture(texture_file)
        glPushMatrix()
        glLoadMatrixd(view_matrix)
        glutSolidTeapot(-.5,20,-20)
        glPopMatrix()


########################################################################

if __name__ == "__main__":
        main()
