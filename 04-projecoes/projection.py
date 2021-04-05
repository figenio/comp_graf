#!/usr/bin/env python3

## @file projection.py
#  Applies an orthographic projection to draw a cube.
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


## Window width.
win_width  = 600
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
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

out vec3 vColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    vColor = color;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

in vec3 vColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(vColor, 1.0f);
} 
"""

## Drawing function.
#
# Draws primitive.
def display():

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUseProgram(program)
    gl.glBindVertexArray(VAO)

    # Define model matrix.
    Rx = ut.matRotateX(np.radians(-30.0))
    T  = ut.matTranslate(0.0, 0.0, -1.0)
    model = np.matmul(T,Rx)

    # Retrieve location of model variable in shader.
    loc = gl.glGetUniformLocation(program, "model")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, model.transpose())

    # Define view matrix.
    view = ut.matTranslate(0.0, 0.0, -3.0)

    #view = ut.matIdentity()
    # Retrieve location of view variable in shader.
    loc = gl.glGetUniformLocation(program, "view")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())
    
    # Define projection matrix.
    projection = ut.matOrtho(-2.0, 2.0,-2.0, 2.0, 0.1, 100.0)

    # Retrieve location of projection variable in shader.
    loc = gl.glGetUniformLocation(program, "projection")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, projection.transpose())

    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

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
    # global mode

    if key == b'\x1b'or key == b'q':
        sys.exit( )

    glut.glutPostRedisplay()


## Init vertex data.
#
# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO
    global VBO

    # Set cube vertices.
    vertices = np.array([
        #Front face first triangle.
        # coordinate       # color
        -0.5, -0.5,  0.5,  0.0, 0.0, 1.0,
         0.5, -0.5,  0.5,  0.0, 0.0, 1.0,
         0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
        #Front face second triangle.
        -0.5, -0.5,  0.5,  0.0, 0.0, 1.0,
         0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
        -0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
        # Right face first triangle.
         0.5, -0.5,  0.5,  0.0, 1.0, 0.0,
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,
         0.5,  0.5, -0.5,  0.0, 1.0, 0.0,
        # Right face second triangle.
         0.5, -0.5,  0.5,  0.0, 1.0, 0.0,
         0.5,  0.5, -0.5,  0.0, 1.0, 0.0,
         0.5,  0.5,  0.5,  0.0, 1.0, 0.0,
        # Back face first triangle.
         0.5, -0.5, -0.5,  0.0, 1.0, 1.0,
        -0.5, -0.5, -0.5,  0.0, 1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0, 1.0, 1.0,
        # Back face second triangle.
         0.5, -0.5, -0.5,  0.0, 1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0, 1.0, 1.0,
         0.5,  0.5, -0.5,  0.0, 1.0, 1.0,
        # Left face first triangle.
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,
        -0.5, -0.5,  0.5,  1.0, 0.0, 0.0,
        -0.5,  0.5,  0.5,  1.0, 0.0, 0.0,
        # Left face second triangle.
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,
        -0.5,  0.5,  0.5,  1.0, 0.0, 0.0,
        -0.5,  0.5, -0.5,  1.0, 0.0, 0.0,
        # Top face first triangle.
        -0.5,  0.5,  0.5,  1.0, 0.0, 1.0,
         0.5,  0.5,  0.5,  1.0, 0.0, 1.0,
         0.5,  0.5, -0.5,  1.0, 0.0, 1.0,
        # Top face second triangle.
        -0.5,  0.5,  0.5,  1.0, 0.0, 1.0,
         0.5,  0.5, -0.5,  1.0, 0.0, 1.0,
        -0.5,  0.5, -0.5,  1.0, 0.0, 1.0,
        # Bottom face first triangle.
        -0.5, -0.5,  0.5,  1.0, 1.0, 1.0,
        -0.5, -0.5, -0.5,  1.0, 1.0, 1.0,
         0.5, -0.5,  0.5,  1.0, 1.0, 1.0,
        # Bottom face second triangle.
        -0.5, -0.5, -0.5,  1.0, 1.0, 1.0,
         0.5, -0.5, -0.5,  1.0, 1.0, 1.0,
         0.5, -0.5,  0.5,  1.0, 1.0, 1.0
    ], dtype='float32')

    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, c_void_p(3*vertices.itemsize))
    gl.glEnableVertexAttribArray(1)
    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)

    # Enable depth test.
    gl.glEnable(gl.GL_DEPTH_TEST);

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
    glut.glutInitContextVersion(3, 3);
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE);
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Orthographic Projection')

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
