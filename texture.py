import cv2 as cv
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys


#window dimensions
width = 1280
height = 720
nRange = 1.0

global capture
capture = None

def cv2array(im):
  depth2dtype = {
    cv.IPL_DEPTH_8U: 'uint8',
    cv.IPL_DEPTH_8S: 'int8',
    cv.IPL_DEPTH_16U: 'uint16',
    cv.IPL_DEPTH_16S: 'int16',
    cv.IPL_DEPTH_32S: 'int32',
    cv.IPL_DEPTH_32F: 'float32',
    cv.IPL_DEPTH_64F: 'float64',
    }

  arrdtype=im.depth
  a = np.fromstring(
     im.tostring(),
     dtype=depth2dtype[im.depth],
     count=im.width*im.height*im.nChannels)
  a.shape = (im.height,im.width,im.nChannels)
  return a

def init():
  #glclearcolor (r, g, b, alpha)
  glClearColor(0.0, 0.0, 0.0, 1.0)

  glutDisplayFunc(display)
  glutReshapeFunc(reshape)
  glutKeyboardFunc(keyboard)
  glutIdleFunc(idle)

def idle():
  #capture next frame

  global capture
  image = cv.QueryFrame(capture)
  image_size = cv.GetSize(image)
  cv.Flip(image, None, 0)
  cv.Flip(image, None, 1)
  cv.CvtColor(image, image, cv.CV_BGR2RGB)
  #you must convert the image to array for glTexImage2D to work
  #maybe there is a faster way that I don't know about yet...
  image_arr = cv2array(image)
  #print image_arr


  # Create Texture
  glTexImage2D(GL_TEXTURE_2D,
    0,
    GL_RGB,
    image_size[0],
    image_size[1],
    0,
    GL_RGB,
    GL_UNSIGNED_BYTE,
    image_arr)

  glutPostRedisplay()

def display():
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
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
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()

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

  glFlush()
  glutSwapBuffers()

def reshape(w, h):
  if h == 0:
    h = 1

  glViewport(0, 0, w, h)
  glMatrixMode(GL_PROJECTION)

  glLoadIdentity()
  # allows for reshaping the window without distoring shape

  if w <= h:
    glOrtho(-nRange, nRange, -nRange*h/w, nRange*h/w, -nRange, nRange)
  else:
    glOrtho(-nRange*w/h, nRange*w/h, -nRange, nRange, -nRange, nRange)

  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()

def keyboard(key, x, y):
  global anim
  if key == chr(27):
    sys.exit()

def main():
  global capture
  #start openCV capturefromCAM
  capture = cv.CaptureFromCAM(0)
  print capture
  cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, width)
  cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, height)

  glutInit(sys.argv)
  glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
  glutInitWindowSize(width, height)
  glutInitWindowPosition(100, 100)
  glutCreateWindow("OpenGL + OpenCV")

  init()
  glutMainLoop()

main()
