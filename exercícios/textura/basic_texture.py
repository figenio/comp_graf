#!/usr/bin/env python3

## @file rectangle.py
#  Draws a rectangle.
# 
#  Draws a rectangle defined with two triangles. The polygon mode can be changed using keys:
#  1 wireframe;
#  2 polygon.
#
# @author Ricardo Dutra da Silva


import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
sys.path.append('../lib/')
import utils as ut

from ctypes import c_void_p
from PIL import Image


## Window width.
win_width  = 800
## Window height.
win_height = 600

## Program variable.
program = None
## Vertex array object.
VAO = None
## Vertex buffer object.
VBO = None

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
layout (location = 2) in vec2 aTexCoord;

out vec3 ourColor;
out vec2 TexCoord;

void main()
{
    gl_Position = vec4(aPos, 1.0);
    ourColor = aColor;
    TexCoord = aTexCoord;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core
out vec4 FragColor;
  
in vec3 ourColor;
in vec2 TexCoord;

uniform sampler2D ourTexture;

void main()
{
    FragColor = texture(ourTexture, TexCoord);
}
"""

## Drawing function.
#
# Draws primitive.
def display():

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    gl.glUseProgram(program)
    gl.glBindVertexArray(VAO)
    #gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
    gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)

    glut.glutSwapBuffers()


## Reshape function.
# 
# Called when window is resized.
#
# @param width New window width.
# @param height New window height.
def reshape(width,height):

    win_width = width
    win_height = height
    gl.glViewport(0, 0, win_width, win_height)
    glut.glutPostRedisplay()


## Keyboard function.
#
# Called to treat pressed keys.
#
# @param key Pressed key.
# @param x Mouse x coordinate when key pressed.
# @param y Mouse y coordinate when key pressed.
def keyboard(key, x, y):

    # global type_primitive

    if key == b'\x1b'or key == b'q':
        sys.exit( )
    if key == b'1':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
    if key == b'2':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    glut.glutPostRedisplay()


## Init vertex data.
#
# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO
    global VBO

    img = Image.open('exercícios/textura/images/wall.jpg')
    print('opened file: size=', img.size, 'format=', img.format)
    imageData = np.array(list(img.getdata()), np.uint8)


    # Set vertices.
    vertices = np.array([
        # positions        colors           texture coords
         0.5,  0.5, 0.0,   1.0, 0.0, 0.0,   1.0, 1.0,   # top right
         0.5, -0.5, 0.0,   0.0, 1.0, 0.0,   1.0, 0.0,   # bottom right
        -0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   0.0, 0.0,   # bottom left
        -0.5,  0.5, 0.0,   1.0, 1.0, 0.0,   0.0, 1.0    # top left 
    ], dtype='float32')
    
    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

   
    textureID = gl.glGenTextures(1) #busca um id
    gl.glBindTexture(gl.GL_TEXTURE_2D, textureID)# Realiza o bind da textura
    # Define parametros de "utilização" da textura
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.size[0], img.size[1], 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, imageData) # Carrega a imagem na textura
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
    img.close() # Libera a imagem da memória

    # Set attributes.
    # VERTEX
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    # COLOR
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * vertices.itemsize, c_void_p(6*vertices.itemsize))
    gl.glEnableVertexAttribArray(1)
    # TEXTURE
    gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 8 * vertices.itemsize, c_void_p(6*vertices.itemsize))
    gl.glEnableVertexAttribArray(2)
    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)

## Create program (shaders).
#
# Compile shaders and create programs.
def initShaders():

    global program

    program = ut.createShaderProgram(vertex_code, fragment_code)


## Main function.
#
# Init GLUT and the window settings. Also, defines the callback functions used in the program.
def main():

    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Rectangle')

    # Init vertex data for the triangle.
    initData()
    
    # Create shaders.
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
