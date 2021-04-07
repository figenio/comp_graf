#!/usr/bin/python

import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import utils as ut

sys.path.append('../lib/')

from ctypes import c_void_p


### --- VARIÁVEIS GLOBAIS --- ###

## Largura da janela
win_width  = 800
## Altura da janela
win_height = 600
## Modo de exibição 
mode = False    # (False, Faces) (True, Arestas)
## Modo de operção
operation = '' # (1, Neutro) (2, Translação) (3, Escala) (4, Rotação)
## Array de vertices
vertices = np.array([], dtype='float32')
## Array de faces
faces = np.array([], dtype='uint32')
## Contagem de vertices
num_element_vertices = 0
## Matriz de transformações iniciada como matriz identidade
M = np.identity(4, dtype='float32')
## Abertura de FOVY
fovy = np.radians(60)
## Intervalor do y
range_y = 0


## Variável do programa
program = None
## Vertex Array Object
VAO = None
## Vertex Buffer Object
VBO = None

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
uniform mat4 transform;
uniform mat4 projection;
uniform mat4 view;
void main()
{
    gl_Position = projection * view * transform * vec4(position, 1.0);
}
"""

## Fragment shader.
fragment_code = """
#version 330 core
out vec4 FragColor;
void main()
{
    FragColor = vec4(0.7f, 0.7f, 0.7f, 1.0f);
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

    # Aplicação das transformações
    loc = gl.glGetUniformLocation(program, "transform")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())

    # Definição da visão
    z_near = range_y/np.tan(fovy)
    view = ut.matTranslate(0.0, 0.0, -z_near-1)
    loc = gl.glGetUniformLocation(program, "view")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())

    # Aplicação da projeção
    projection = ut.matPerspective(fovy, win_width/win_height, 0.1, 150)
    #projection = ut.matOrtho(-1, 1, -2, 2, 0.1, 10)
    loc = gl.glGetUniformLocation(program, "projection")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, projection.transpose())

    gl.glDrawElements(gl.GL_TRIANGLES, num_element_vertices, gl.GL_UNSIGNED_INT, None)

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

def special_keyboard(key, x, y):
    handle_operation(key)

## Keyboard function.
#
# Called to treat pressed keys.
#
# @param key Pressed key.
# @param x Mouse x coordinate when key pressed.
# @param y Mouse y coordinate when key pressed.
def keyboard(key, x, y):
    
    global mode, operation
    
    # Seleção de operação
    if key == b't':
        operation = 'translate'
        print('translate')
    elif key == b'r':
        operation ='rotate'
        print('rotate')
    elif key == b'e':
        operation ='scale'
        print('scale')
    elif key == b'v':
        mode = not mode
        if mode:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        else:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        glut.glutPostRedisplay()
    else:
        handle_operation(key)


def handle_operation(key):
    global operation
    print("operation")

    if operation == 'translate':
        if key == glut.GLUT_KEY_UP:
            translate(0.0, 0.05, 0.0)
        elif key == glut.GLUT_KEY_DOWN:
            translate(0.0, -0.05, 0.0)
        elif key == glut.GLUT_KEY_RIGHT:
            translate(0.05, 0.0, 0.0)
        elif key == glut.GLUT_KEY_LEFT:
            translate(-0.05, 0.0, 0.0)
        elif key == b'a':
            translate(0.0, 0.0, 0.5)
        elif key == b'd':
            translate(0.0, 0.0, -0.5)

    elif operation == 'rotate':
        angle = 10.0
        if key == glut.GLUT_KEY_UP:
            rotate('x', angle)
        elif key == glut.GLUT_KEY_DOWN:
            rotate('x', -angle)
        elif key == glut.GLUT_KEY_RIGHT:
            rotate('y', angle)
        elif key == glut.GLUT_KEY_LEFT:
            rotate('y', -angle)
        elif key == b'a':
            rotate('z', angle)
        elif key == b'd':
            rotate('z', -angle)
    
    elif operation == 'scale':
        coeff=0.05

        if key == glut.GLUT_KEY_UP:
            scale(1, 1+coeff, 1)
        elif key == glut.GLUT_KEY_DOWN:
            scale(1, 1-coeff, 1)
        elif key == glut.GLUT_KEY_RIGHT:
            scale(1+coeff, 1, 1)
        elif key == glut.GLUT_KEY_LEFT:
            scale(1-coeff, 1, 1)
        elif key == b'a':
            scale(1, 1, 1+coeff)
        elif key == b'd':
            scale(1, 1, 1-coeff)

    glut.glutPostRedisplay()

def translate(x, y, z):
    global M
    T = ut.matTranslate(x, y, z)
    M = np.matmul(T,M)


def scale(x, y, z):
    global M
    S = ut.matScale(x, y, z)
    M = np.matmul(S,M)


def rotate(axis, angle=10.0):
    global M

    if axis == 'x':
        R = ut.matRotateX(np.radians(angle))
    elif axis == 'y':
        R = ut.matRotateY(np.radians(angle))
    elif axis == 'z':
        R = ut.matRotateZ(np.radians(angle))

    M = np.matmul(R,M)


def load_obj():
    obj_name = sys.argv[1]
    obj_file = open(obj_name)
    print("Input argument:", obj_name)

    global vertices
    global faces
    global num_element_vertices
    global range_y

    # For que itera nas linha do arquivo
    for line in obj_file:
        # Caso a linha descreva um vértice
        # print("Line:", line)
        if line[:2] == "v ":
            v1_index = line.find(" ") + 1 # a posição do primeiro vértice
            v2_index = line.find(" ", v1_index) + 1 # a posição do próximo vértice a partir da última conhecida
            v3_index = line.find(" ", v2_index) + 1

            # Lê e converte os valores do arquivo para float
            vertice = np.array([float(line[v1_index:(v2_index-1)]),
                        float(line[v2_index:(v3_index-1)]),
                        float(line[v3_index:-1])],
                        dtype='float32')
            
            # Adiciona o novo vértice ao array de vértices
            vertices = np.append(vertices, vertice)

        # Caso a linha descreva uma face
        elif line[:2] == 'f ':
            # Encontra a posição dos valores dos vértica de uma face
            f1_index = line.find(" ") + 1
            f2_index = line.find(" ", f1_index + 1)
            f3_index = line.find(" ", f2_index + 1)

            # Separa a string com os valores de cada vértice que compões a face
            f1_values = line[f1_index:(f2_index)]
            f2_values = line[f2_index:(f3_index)]
            f3_values = line[f3_index:-1]

            # Separa os valores de vértice, cor e normal que compões a face
            f1_vertice = f1_values.split('/')[0]
            # f1_color = f1_values.split('/')[1]
            # f1_normal = f1_values.split('/')[2]
            # print("Vertice:", f1_vertice)
            
            f2_vertice = f2_values.split('/')[0]
            # f2_color = f2_values.split('/')[1]
            # f2_normal = f2_values.split('/')[2]
            # print("Vertice:", f2_vertice)

            f3_vertice = f3_values.split('/')[0]
            # f3_color = f3_values.split('/')[1]
            # f3_normal = f3_values.split('/')[2]
            # print("Vertice:", f3_vertice)

            nova_face = np.array([int(f1_vertice)-1,
                int(f2_vertice)-1,
                int(f3_vertice)-1],
                dtype='uint32')

            faces = np.append(faces, nova_face)

    num_element_vertices = len(faces)

    max_v = np.max(vertices)
    min_v = np.min(vertices)
    range_y = max_v - min_v


    print("Vertices:\n", vertices)
    print("Faces:\n", faces)
    print("Número de vértices", num_element_vertices)



def initData():

    global VAO
    global vertices
    global faces
    
    # Chama o método que vai ler o arquivo de entrada
    load_obj()


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
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    gl.glEnableVertexAttribArray(0)

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)
    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)



def initShaders():

    global program
    program = ut.createShaderProgram(vertex_code, fragment_code)


def main():

    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Mesh Viwer')

    initData()
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutSpecialFunc(special_keyboard)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()