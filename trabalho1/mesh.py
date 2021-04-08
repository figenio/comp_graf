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
operation = ''
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
## Coordenadas do centro do objeto
obj_center = [0, 0, 0]
## Coordenadas máximas e mínimas do objeto em cada eixo
x_min = sys.float_info.max
y_min = sys.float_info.max
z_min = sys.float_info.max
x_max = sys.float_info.min
y_max = sys.float_info.min
z_max = sys.float_info.min

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

    gl.glBindVertexArray(VAO)
    gl.glUseProgram(program)

    # Atribuição da matris de transformações
    print("Matriz de transforamação:\n", M)
    loc = gl.glGetUniformLocation(program, "transform")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())


    # View
    # z_near = z_min + (y_max-y_min)/np.tan(fovy)
    z_near = (y_max-y_min)*4.0/np.tan(fovy)
    print(z_near)

    view = ut.matTranslate(0.0, 0.0, z_near)
    # view = ut.matTranslate(0.0, 0.0, z_near-1)

    loc = gl.glGetUniformLocation(program, "view")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())

    # Projection
    # projection = ut.matOrtho(x_min*1.5, x_max*1.5, y_min*1.5, y_max*1.5, 0.1, 500)
    projection = ut.matPerspective(fovy, win_width/win_height, 0.1, 300)
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
    unit = 0.01*max(x_max, y_max, z_max)

    if operation == 'translate':
        if key == glut.GLUT_KEY_UP:
            translate(0.0, unit, 0.0)
        elif key == glut.GLUT_KEY_DOWN:
            translate(0.0, -unit, 0.0)
        elif key == glut.GLUT_KEY_RIGHT:
            translate(unit, 0.0, 0.0)
        elif key == glut.GLUT_KEY_LEFT:
            translate(-unit, 0.0, 0.0)
        elif key == b'a':
            translate(0.0, 0.0, unit)
        elif key == b'd':
            translate(0.0, 0.0, -unit)

    elif operation == 'rotate':
        angle = 1.0
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
        coeff=0.01

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
    global M, obj_center
    T = ut.matTranslate(x, y, z)
    M = np.matmul(T,M)

    obj_center[0] += x
    obj_center[1] += y
    obj_center[2] += z


def scale(x, y, z):
    global M
    x_center, y_center, z_center = obj_center[0], obj_center[1], obj_center[2]

    translate(-x_center, -y_center, -z_center)
    S = ut.matScale(x, y, z)
    M = np.matmul(S,M)
    translate( x_center, y_center, z_center)


def rotate(axis, angle=10.0):
    global M
    x, y, z = obj_center[0], obj_center[1], obj_center[2]

    translate(-x, -y, -z)

    if axis == 'x':
        R = ut.matRotateX(np.radians(angle))
    elif axis == 'y':
        R = ut.matRotateY(np.radians(angle))
    elif axis == 'z':
        R = ut.matRotateZ(np.radians(angle))

    M = np.matmul(R,M)

    translate(x, y, z)


def load_obj():
    obj_name = sys.argv[1]
    obj_file = open(obj_name)
    print("Input argument:", obj_name)

    global vertices
    global faces
    global num_element_vertices
    global range_y
    global obj_center

    # Limites máximos do objeto
    global x_min
    global y_min
    global z_min
    global x_max
    global y_max
    global z_max

    faces_list = list() # Lista temporária para salvar as faces

    # For que itera nas linha do arquivo
    for line in obj_file:
        # Caso a linha descreva um vértice
        if line[:2] == "v ":
            # Cada coordenada de vértice é separada e adicionada ao array de vértices
            v_values = line[1:].split()
            vertices = np.append(vertices, np.asarray(v_values, dtype='float32'))

            # Validamos se algumas das coordenadas é um ponto mais extremo do objeto
            if float(v_values[0]) > x_max:
                x_max = float(v_values[0])
            if float(v_values[0]) < x_min:
                x_min = float(v_values[0])
            if float(v_values[1]) > y_max:
                y_max = float(v_values[1])
            if float(v_values[1]) < y_min:
                y_min = float(v_values[1])
            if float(v_values[2]) > z_max:
                z_max = float(v_values[2])
            if float(v_values[2]) < z_min:
                z_min = float(v_values[2])


        # Caso a linha descreva uma face
        elif line[:2] == 'f ':
            # Cada valor de face é separado
            f_values = line[1:].split()

            for v in f_values:
                if '/' in v: # Caso hajam mais valores do que apenas o índice da coordenada
                    v_index  = v.split('/')[0] # Separamos o valor da coordenada
                    # v_color  = v.split('/')[1]
                    # v_normal = v.split('/')[2]
            
                    # Atribuimos o valor da coordenada da face à lista de faces
                    if v_index:
                        faces = faces_list.append(int(v_index)-1)
                    # if vt:
                    #     np.append(int(vt))
                    # if v_normal:
                    #     np.append(int(vn))
                else: faces_list.append(int(v)-1)

    # Atribuímos a lista de faces para o array no formato int
    faces = np.asarray(faces_list, dtype='uint32')

    v_max = np.max(vertices)
    vertices = vertices/v_max
    x_min = x_min/v_max
    y_min = y_min/v_max
    z_min = z_min/v_max
    x_max = x_max/v_max
    y_max = y_max/v_max
    z_max = z_max/v_max

    # As coordenadas de centro recebem o ponto médio dos mínimos e máximos do objeto em cada eixo
    obj_center = [(x_max-x_min)/2, (y_max-y_min)/2, (z_max-z_min)/2]

    num_element_vertices = len(faces)

    # print("Vertices:\n", vertices)
    # print("Faces:\n", faces)
    # print("Número de vértices", num_element_vertices)
    print("Coordenadas do centro do objeto", obj_center)



def initData():

    global VAO
    global vertices
    global faces
    global obj_center
    global M
    
    # Chama o método que vai ler o arquivo de entrada
    load_obj()
    
    # Primeira translação para levar o centro do objeto para a origem dos eixos
    T = ut.matTranslate(-obj_center[0], -obj_center[1], -obj_center[2])
    M = np.matmul(T,M)

    obj_center[0] -= obj_center[0]
    obj_center[1] -= obj_center[1]
    obj_center[2] -= obj_center[2]


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
    obj_name = sys.argv[1]
    if '.obj' in obj_name:
        main()
        # load_obj()
    else: print("Not a .obj file")