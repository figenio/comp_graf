#!/usr/bin/env python3

import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
sys.path.append('../lib/')
import utils as ut
from ctypes import c_void_p


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

## Rotation angle.
angle = 0.0
## Rotation increment.
angle_inc = 0.05
## Rotation mode.
mode = 1
## Transform Matrix
M = np.identity(4, dtype='float32')

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

out vec3 vColor;

uniform mat4 transform;

void main()
{
    gl_Position = transform * vec4(position, 1.0);
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
    global M

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUseProgram(program)
    gl.glBindVertexArray(VAO)

    # Retrieve location of tranform variable in shader.
    loc = gl.glGetUniformLocation(program, "transform")
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())

    #gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
    gl.glDrawElements(gl.GL_TRIANGLES, 36, gl.GL_UNSIGNED_INT, None)

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

    global type_primitive
    global mode

    # Primeiro verifica modo de exibição
    if key == b'\x1b':
        sys.exit( )
    if key == b'1':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE) # Linhas
        mode = 1
    if key == b'2':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL) # Preenchido
        mode = 2
    if key == b'3':
        mode = 3 # Rotação X constante
    if key == b'4':
        mode = 4 # Rotação Y constante
    if key == b'5':
        mode = 5 # Rotação Z constante

    # TRANSFORMAÇÕES
    #
    # Translação
    if key == b'a':   # Esquerda
        translation(-0.05, 0.0, 0.0)
    if key == b'd':   # Direita
        translation(0.05, 0.0, 0.0)
    if key == b'w':   # Cima
        translation(0.0, 0.05, 0.0)
    if key == b's':   # Baixo
        translation(0.0, -0.05, 0.0)

    # Escalando
    if key == b'u': # Aumentar largura
        scaling(1.05, 1.00, 1.00)
    if key == b'i': # Aumentar altura
        scaling(1.00, 1.05, 1.00)
    if key == b'o': # Aumentar profundidade
        scaling(1.0, 1.00, 1.05)
    if key == b'j': # Diminuir largura
        scaling(0.95, 1.00, 1.00)
    if key == b'k': # Diminuir largura
        scaling(1.00, 0.95, 1.00)
    if key == b'l': # Diminuir largura
        scaling(1.00, 1.00, 0.95)
    if key == b'+': # Aumentar TUDO
        scaling(1.05, 1.05, 1.05)
    if key == b'-': # Diminuir TUDO
        scaling(1.05, 1.05, 1.05)
    
    # Rotação
    if key == b'x':
        rotation('x')
    if key == b'y':
        rotation('y')
    if key == b'z':
        rotation('z')
    

    glut.glutPostRedisplay()


# Método que caclula a translação do cubo em e, y e z
def translation(x, y, z):
    global M

    T = ut.matTranslate(x, y, z) # Configura a matriz de translação com os valores
    M = np.matmul(T,M) # Multiplica a matriz T pela "geral" M
    glut.glutPostRedisplay() # Chama a redisplay para redesenhar

# Método que calcula a escala do cubo em x, y e z
def scaling(x, y, z):
    global M

    S = ut.matScale(x, y, z) # Gera a matriz de scala com os valores
    M = np.matmul(S,M) # Multiplica a matriz S pela "geral" M
    glut.glutPostRedisplay() # Chama a redisplay para redesenhar

def rotation(axis, angle=10.0):
    global M

    if axis == 'x':
        R = ut.matRotateX(np.radians(angle))
    if axis == 'y':
        R = ut.matRotateY(np.radians(angle))
    if axis == 'z':
        R = ut.matRotateZ(np.radians(angle))

    M = np.matmul(R,M)
    glut.glutPostRedisplay()




## Idle function.
#
# Called continuously.
# idle foi definida para continuar a incrementar o ângulo em determinado modo de execição do programa
def idle():
    global angle

    if mode == 3:
        angle = angle+angle_inc if (angle+angle_inc) < 360.0 else (360.0-angle+angle_inc)

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
        # coordinate        color
        -0.5, -0.5, -0.5,   0.58, 0.92, 0.86, # 0
        -0.5, -0.5,  0.5,   0.48, 0.80, 0.83, # 1
        -0.5,  0.5, -0.5,   0.48, 0.83, 0.66, # 2
        -0.5,  0.5,  0.5,   0.56, 0.96, 1.00, # 3
         0.5, -0.5, -0.5,   0.58, 0.92, 0.86, # 4
         0.5, -0.5,  0.5,   0.48, 0.80, 0.83, # 5
         0.5,  0.5, -0.5,   0.48, 0.83, 0.66, # 6
         0.5,  0.5,  0.5,   0.56, 0.96, 1.00  # 7
    ], dtype='float32')
    
    # Set cube faces with indexes
    indices = np.array([
        1, 3, 5, 7, 3, 5, # Face Front
        1, 0, 3, 2, 0, 3, # Face Left
        0, 4, 2, 6, 4, 2, # Face Back
        5, 4, 7, 6, 4, 7, # Face Right
        3, 2, 7, 6, 2, 7, # Face Up
        1, 0, 5, 4, 0, 5  # Face Down
    ], dtype="uint32")

    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

    # Element Buffer Object 
    EBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, c_void_p(3*vertices.itemsize))
    gl.glEnableVertexAttribArray(1)

    # Enables depht test and sets it
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)
    
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
    glut.glutCreateWindow('Cube')

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
