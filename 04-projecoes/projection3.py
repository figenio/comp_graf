#!/usr/bin/env python3

## @file projection3.py
# Applies a perspective projection to draw a cube and a pyramid.
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
VAO1 = None
## Vertex buffer object.
VBO1 = None
## Vertex array object.
VAO2 = None
## Vertex buffer object.
VBO2 = None

## Pyramid x angle
px_angle = 0.0
## Pyramid x angle increment
px_inc = 0.01
## Pyramid y angle
py_angle = 0.0
## Pyramid y angle increment
py_inc = 0.02

## Cube x angle
cx_angle = 0.0
## Cube x angle increment
cx_inc = 0.01
## Cube y angle (orbit)
cy_angle = 0.0
## Cube y angle increment
cy_inc = 0.03
## Cube z angle
cz_angle = 0.0
## Cube z angle increment
cz_inc = 0.02


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

    # Define view matrix.
    view = ut.matTranslate(0.0, 0.0, -3.0)

    # Retrieve location of view variable in shader.
    loc = gl.glGetUniformLocation(program, "view")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())
    
    # Define projection matrix.
    projection = ut.matPerspective(np.radians(60.0), win_width/win_height, 0.1, 100.0)

    # Retrieve location of projection variable in shader.
    loc = gl.glGetUniformLocation(program, "projection")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, projection.transpose())

    # Pyramid.
    gl.glBindVertexArray(VAO2)

    # Define model matrix.
    S = ut.matScale(0.5, 0.5, 0.5)
    Rx = ut.matRotateX(np.radians(px_angle))
    Ry = ut.matRotateY(np.radians(py_angle))
    T  = ut.matTranslate(0.0, -0.0, -1.0)
    model = np.matmul(Rx,S)
    model = np.matmul(Ry,model)
    model = np.matmul(T,model)

    # Retrieve location of model variable in shader.
    loc = gl.glGetUniformLocation(program, "model")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, model.transpose())

    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 12)


    # Cube.
    gl.glBindVertexArray(VAO1)

    # Define model matrix.
    S = ut.matScale(0.3, 0.3, 0.3)
    Rx = ut.matRotateX(np.radians(cx_angle))
    Ry = ut.matRotateY(np.radians(cy_angle))
    Rz = ut.matRotateZ(np.radians(cz_angle))
    T  = ut.matTranslate(0.0, 0.0, -2.0)
    model = np.matmul(Rz,S)
    model = np.matmul(Rx,model)
    model = np.matmul(T,model)
    model = np.matmul(Ry,model)
    model = np.matmul(T,model)

    # Retrieve location of model variable in shader.
    loc = gl.glGetUniformLocation(program, "model")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, model.transpose())

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
    gl.glViewport(0, 0, width, height)
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


## Idle function.
#
# Called continuously.
def idle():
    global px_angle
    global py_angle
    global cx_angle
    global cy_angle
    global cz_angle

    px_angle = px_angle+px_inc if (px_angle+px_inc) < 360.0 else (360.0-px_angle+px_inc)
    py_angle = py_angle+py_inc if (py_angle+py_inc) < 360.0 else (360.0-py_angle+py_inc)
    
    cx_angle = cx_angle+cx_inc if (cx_angle+cx_inc) < 360.0 else (360.0-cx_angle+cx_inc)
    cy_angle = cy_angle+cy_inc if (cy_angle+cy_inc) < 360.0 else (360.0-cy_angle+cy_inc)
    cz_angle = cz_angle+cz_inc if (cz_angle+cz_inc) < 360.0 else (360.0-cz_angle+cz_inc)

    glut.glutPostRedisplay()


## Init vertex data.
#
# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO1
    global VBO1
    global VAO2
    global VBO2

    # Set cube vertices.
    cube = np.array([
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
    VAO1 = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO1)

    # Vertex buffer
    VBO1 = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO1)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, cube.nbytes, cube, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*cube.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*cube.itemsize, c_void_p(3*cube.itemsize))
    gl.glEnableVertexAttribArray(1)

    # Set pyramid vertices.
    pyramid = np.array([
        # Front face
        # coordinates     # color
         0.0,  1.0,  0.0, 0.0, 0.0, 1.0,
        -1.0, -1.0,  0.0, 0.0, 0.0, 1.0,
         1.0, -1.0,  0.0, 0.0, 0.0, 1.0,
        # Right face
         1.0, -1.0,  0.0, 0.0, 1.0, 0.0,
         0.0,  1.0,  0.0, 0.0, 1.0, 0.0,
         0.0, -1.0, -1.0, 0.0, 1.0, 0.0,
        # Left face
        -1.0, -1.0,  0.0, 0.0, 1.0, 1.0,
         0.0,  1.0,  0.0, 0.0, 1.0, 1.0,
         0.0, -1.0, -1.0, 0.0, 1.0, 1.0,
        # Bottom face
        -1.0, -1.0,  0.0, 1.0, 0.0, 0.0,
         1.0, -1.0,  0.0, 1.0, 0.0, 0.0,
         0.0, -1.0, -1.0, 1.0, 0.0, 0.0
    ], dtype='float32')

    # Vertex array.
    VAO2 = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO2)

    # Vertex buffer
    VBO2 = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO2)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, pyramid.nbytes, pyramid, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*pyramid.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*pyramid.itemsize, c_void_p(3*pyramid.itemsize))
    gl.glEnableVertexAttribArray(1)
    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)

    # Enable depth test.
    gl.glEnable(gl.GL_DEPTH_TEST)

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
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Perspective Projection')

    # Init vertex data for the triangle.
    initData()
    
    # Create shaders.
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutIdleFunc(idle)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
