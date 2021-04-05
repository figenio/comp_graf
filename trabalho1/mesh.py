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

## Variável do programa
program = None
## Vertex Array Object
VAO = None
## Vertex Buffer Object
VBO = None


def load_obj():
    obj_name = sys.argv[1]
    obj_file = open(obj_name)

    global vertices
    global faces

    for line in obj_file:
        if line[:2] == "v ":
            v1_index = line.find(" ") + 1 # a posição seguinte ao primeiro espaço
            v2_index = line.find(" ", v1_index + 1) # a partir de onde encontrou o último vértice, procura o próximo
            v3_index = line.find(" ", v2_index + 1)

            # Converte os valores para float e atribui a um vértice
            vertice = np.array([float(line[v1_index:v2_index]),
                        float(line[v2_index:v3_index]),
                        float(line[v3_index:-1])],
                        dtype='float32')
            print(vertice)
            vertices = np.append(vertices,vertice)
        elif line[:2] == 'f ':
            f1_index = line.find(" ") + 1 # a posição seguinte ao primeiro espaço
            f2_index = line.find(" ", v1_index + 1) # a partir de onde encontrou o último vértice, procura o próximo
            f3_index = line.find(" ", v2_index + 1)

    print("Vertices:\n", vertices)





if __name__ == '__main__':
    obj_name = sys.argv[1]
    print("Input argument:", obj_name)
    load_obj()