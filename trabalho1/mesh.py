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
mode = 1    # (1, Faces) (2, Arestas)
## Modo de operção
operation = 1 # (1, Neutro) (2, Translação) (3, Escala) (4, Rotação)
## Array de vertices
vertices = np.array(0)
## Array de faces
faces = np.array(0)
## Contagem de vertices
num_vertices

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


def display():

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUseProgram(program)
    
    gl.glBindVertexArray(VAO)

    # Transformations
    loc = gl.glGetUniformLocation(program, "transform")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())

    # View
    z_near = range_y/np.tan(fovy)
    view = ut.matTranslate(0.0, 0.0, -z_near-1)
    loc = gl.glGetUniformLocation(program, "view")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())

    # Projection
    projection = ut.matPerspective(fovy, win_width/win_height, 0.1, 150)
    #projection = ut.matOrtho(-1, 1, -2, 2, 0.1, 10)
    loc = gl.glGetUniformLocation(program, "projection")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, projection.transpose())

    gl.glDrawElements(gl.GL_TRIANGLES, count_vertices, gl.GL_UNSIGNED_INT, None)
    #######num_vertices

    glut.glutSwapBuffers()


def load_obj():
    obj_name = sys.argv[1]
    obj_file = open(obj_name)

    global vertices
    global faces

    # For que itera nas linha do arquivo
    for line in obj_file:
        # Caso a linha descreva um vértice
        if line[:2] == "v ":
            v1_index = line.find(" ") + 1 # a posição do primeiro vértice
            v2_index = line.find(" ", v1_index + 1) # a posição do próximo vértice a partir da última conhecida
            v3_index = line.find(" ", v2_index + 1)

            # Lê e converte os valores do arquivo para float
            vertice = np.array([float(line[v1_index:(v2_index-2)]),
                        float(line[v2_index:(v3_index-2)]),
                        float(line[v3_index:-1])],
                        dtype='float32')
            
            # Adiciona o novo vértice ao array de vértices
            vertices = np.append(vertices,vertice)

        # Caso a linha descreva uma face
        elif line[:2] == 'f ':
            # Encontra a posição dos valores dos vértica de uma face
            print("Line:", line)
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

            nova_face = np.array([int(f1_vertice),
                int(f2_vertice),
                int(f3_vertice)],
                dtype='float32')

            faces = np.append(faces, nova_face)

    print("Vertices:\n", vertices)
    print("Faces:\n", faces)





if __name__ == '__main__':
    obj_name = sys.argv[1]
    print("Input argument:", obj_name)
    load_obj()