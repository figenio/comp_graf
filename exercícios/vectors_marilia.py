#!/usr/bin/env python3

## @file primitives.py
#  Draws different primitives.
# 
#  Draws different primitives of OpenGL according to a pressed key:
#  1 for points;
#  2 for lines;
#  3 for line strip;
#  4 for line loop;
#  5 for triangles;
#  6 for triangle strip;
#  7 for triangle fan.
#
# @author Ricardo Dutra da Silva

import math
import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
sys.path.append('../lib/')
import utils as ut


## Window width.
win_width  = 800
## Window height.
win_height = 600

## Program variable.
program = None

## Vertex array object.
VAO = None

index_count = 4
count = 0
vertices = np.array([
    # Position attribute    
    # -1.0,  0.0, 0.0,        
    #  1.0,  0.0, 0.0,        
    #  0.0, -1.0, 0.0,         
    #  0.0,  1.0, 0.0,        
], dtype='float32')



## Vertex shader.
vertex_code = """
#version 330 core

layout (location = 0) in vec3 position;

void main()
{
    gl_Position = vec4(position.x, position.y, position.z, 1.0);
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0f, 0.0f, 0.0f, 1.0f);
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

    gl.glDrawArrays(gl.GL_LINE_STRIP, 0, 3)

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

## Init vertex data.
#
# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO

    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

    gl.glEnableVertexAttribArray(0)

    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)



## Create program (shaders).
#
# Compile shaders and create programs.
def initShaders():

    global program

    program = ut.createShaderProgram(vertex_code, fragment_code)


# Handling mouse event 
def mouse(button, state, x, y):

    global vertices
    global index_count
    global count 
    points = ['P', 'O', 'Q']

    if state == 1:
        x_coord = x/win_width*2-1
        y_coord = -(y/win_height*2-1)

        vertices = np.append(vertices, [
            x_coord, y_coord, 0.0,    
        ]).astype('float32')

        index_count = vertices.size//3

        print(f"{points[count]}: {x_coord, y_coord}")
        count+=1
        if index_count == 3:
            initData()
            glut.glutPostRedisplay()

            p = vertices[:2]
            o = vertices[3:5]
            q = vertices[6:8]

            u = p - o
            v = q - o

            ex6(u,v,p)
            
            

def dist_ponto_reta(p, v):
    return (prod_vetorial(p-v, v)/magnitude(v))

def angulo(u, v):
    return math.acos(prod_interno(u,v)/(magnitude(u)*magnitude(v)))

def prod_interno(u, v):
    return u[0]*v[0] + u[1]*v[1]

def prod_vetorial(u, v):
    return magnitude(u) * magnitude(v) * np.sin(angulo(u, v))

def magnitude(v):
    return math.sqrt(prod_interno(v, v))

def ex6(u,v,p):
    print()
    print(f"u = {u} \nv = {v}")
    print()
    print("u . v = {:.2f}".format(prod_interno(u, v)))
    print("|u x v| = {:.2f}".format(prod_vetorial(u, v)))
    print()
    print("Ângulo (u, v) = {:.2f} rad \nÂngulo (u, v) = {:.2f} graus".format(angulo(u, v), math.degrees(angulo(u, v))))
    print("Distância (P, v) = {:.2f}".format(dist_ponto_reta(p, v)))

## Main function.
#
# Init GLUT and the window settings. Also, defines the callback functions used in the program.
def main():

    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Vectors')


    # Init vertex data.
    initData()
    
    # Create shaders.
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutMouseFunc(mouse)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
