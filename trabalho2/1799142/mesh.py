#!/usr/bin/python

## @file mesh.py
# Arquivo do trabalho 2 da disciplina de Computação Gráfica,
# onde é implementada iluminação e textura em objetos de arquivo .obj
# 
# @author Mateus Raganhan Figênio


import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import utils as ut

from PIL import Image
from ctypes import c_void_p

sys.path.append('../lib/')


### --- VARIÁVEIS GLOBAIS --- ###

## Largura da janela
win_width  = 800
## Altura da janela
win_height = 600
## Modo de exibição 
mode = False    # (False, Faces) (True, Arestas)
## Modo de operção
operation = ''
## Numpy Vertex Array
vertex_array = np.array([], dtype='float32')
## Número de vértices
vertex_number = None
## Se o obj carregado tem ou não normal
normal = False
## Flag de se o programa vai aplicar ou não a textura
uso_textura = False

## Matriz de transformações iniciada como matriz identidade
M = np.identity(4, dtype='float32')
## Abertura de FOVY
fovy = np.radians(45.0)
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
## Vertex Texture Object
VTO = None

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;

uniform mat4 inverse;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 lightPosition;

out vec3 vNormal;
out vec3 fragPosition;
out vec3 LightPos;
out vec3 TexCoords;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    fragPosition = vec3(view * model * vec4(position, 1.0));
    vNormal = mat3(inverse) * normal;
    LightPos = vec3(view * vec4(lightPosition, 1.0));
    TexCoords = position;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core
in vec3 vNormal;
in vec3 fragPosition;
in vec3 LightPos;
in vec3 TexCoords;

out vec4 fragColor;

uniform vec3 objectColor;
uniform vec3 lightColor;
uniform vec3 cameraPosition;
uniform samplerCube cubemap;
uniform bool texture_flag;

void main()
{
    float ka = 0.5;
    vec3 ambient = ka * lightColor;

    float kd = 0.8;
    vec3 n = normalize(vNormal);
    vec3 l = normalize(LightPos - fragPosition);
    
    float diff = max(dot(n,l), 0.0);
    vec3 diffuse = kd * diff * lightColor;

    float ks = 1.0;
    vec3 v = normalize(cameraPosition - fragPosition);
    vec3 r = reflect(-l, n);

    float spec = pow(max(dot(v, r), 0.0), 3.0);
    vec3 specular = ks * spec * lightColor;

    vec3 light = (ambient + diffuse + specular) * objectColor;  
    fragColor = vec4(light, 1.0);
    if (texture_flag) {
        fragColor = texture(cubemap, TexCoords) * fragColor;
    }
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

    # Aplicação da matriz de transformações no modelo e passando ele para o Vertex Shader
    loc = gl.glGetUniformLocation(program, "model")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())

    # Um cálculo para variar o z de translação da view e da distância de fundo
    # da caixa de projeção, para o tamanho de cada objeto
    z_dist = (y_max-y_min)*4.0/np.tan(fovy)

    # Definição da visão
    view = ut.matTranslate(0.0, 0.0, -z_dist)
    loc = gl.glGetUniformLocation(program, "view")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())

    # Aplicação da projeção
    projection = ut.matPerspective(fovy, win_width/win_height, 0.1, int(z_dist*3))
    loc = gl.glGetUniformLocation(program, "projection")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, projection.transpose())

    # Adjust Normals
    loc = gl.glGetUniformLocation(program, "inverse")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())

    # Object color. (com cor diferente caso não seja ativada a textura)
    loc = gl.glGetUniformLocation(program, "objectColor")
    if uso_textura: gl.glUniform3f(loc, 1.0, 1.0, 1.0)
    else: gl.glUniform3f(loc, 0.8, 0.0, 0.0)
    # Light color.
    loc = gl.glGetUniformLocation(program, "lightColor")
    gl.glUniform3f(loc, 1.0, 1.0, 1.0)
    # Light position.
    loc = gl.glGetUniformLocation(program, "lightPosition")
    gl.glUniform3f(loc, 2*float(x_max), float(y_max), float(z_dist)) # gl.glUniform3f(loc, 1.0, 0.0, 2.0)
    # Camera position.
    loc = gl.glGetUniformLocation(program, "cameraPosition")
    gl.glUniform3f(loc, 0.0, 0.0, 0.0)

    # Binds Texture 
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, VTO)

    # Set texture use
    loc = gl.glGetUniformLocation(program, "texture_flag")
    gl.glUniform1f(loc, uso_textura)

    gl.glDrawArrays(gl.GL_TRIANGLES, 0, vertex_number)
    gl.glBindVertexArray(0)

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

# Method that interprets special keyboard inputs (like arrows)
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
    
    global mode, operation, uso_textura

    # Configuração de textura
    if key == b'1':
        uso_textura = False
        print('Textura desabilitada')
        glut.glutPostRedisplay()
    elif key == b'2':
        uso_textura = True
        print('Textura habilitada')
        glut.glutPostRedisplay()
    # Seleção de operação
    elif key == b't':
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
            translate(0.0, 0.0, 10*unit)
        elif key == b'd':
            translate(0.0, 0.0, -10*unit)

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

# Método que carrega o objeto definido no arquivo obj para o vertex array
def load_obj():
    obj_name = sys.argv[1]
    obj_file = open(obj_name)
    print("Input argument:", obj_name)
    
    # Chamada dos arrays e valores a serem setados pelo objeto
    global vertex_array, vertex_number, normal, M, obj_center
    # Coordenadas limite do objeto
    global x_min, y_min, z_min, x_max, y_max, z_max

    vertices = list()
    normais = list()
    faces = {'v':[], 'n':[]}
    output_vertices = list()

    # LEITURA DO ARQUIVO
    # For que itera nas linha do arquivo
    for line in obj_file:
        # Caso a linha descreva um vértice
        if line[:2] == "v ":
            # Cada coordenada de vértice é separada e adicionada ao array de vértices
            v_values = line[1:].split()
            vertices.append(v_values)

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

        # Caso a linha descreva a normal de um vértice
        elif line[:2] == "vn":
            n_values = line[2:].split()
            normais.append(n_values)

        # Caso a linha descreva uma face
        elif line[:2] == 'f ':
            # Cada valor de face é separado
            f_values = line[1:].split()

            for v in f_values:
                if '/' in v: # Caso hajam mais valores do que apenas o índice da coordenada
                    normal = True
                    v_index  = v.split('/')[0] # Separamos o valor da coordenada
                    # v_color  = v.split('/')[1]
                    v_normal = v.split('/')[2]
            
                    # Atribuimos o valor da coordenada da face à lista de faces
                    if v_index:
                        faces['v'].append(int(v_index)-1)
                    if v_normal:
                        faces['n'].append(int(v_normal)-1)
                else: faces['v'].append(int(v)-1)

    if normal == True:
        for v, n in zip(faces['v'], faces['n']):
            output_vertices.append(vertices[v])
            output_vertices.append(normais[n])
    else:
        for v in faces['v']:
            output_vertices.append(vertices[v])
    
    # As coordenadas de centro recebem o ponto médio dos mínimos e máximos do objeto em cada eixo
    obj_center = [(x_max+x_min)/2, (y_max+y_min)/2, (z_max+z_min)/2]
    vertex_number = len(output_vertices)
    vertex_array = np.asarray(output_vertices, dtype='float32').flatten()

## Init vertex data.
#
# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO, VBO, VTO

    # Usa os array de vertices, faces, matriz de transforamção e centro do objeto
    global vertex_array, normal, M, obj_center
    
    # Chama o método que vai ler o arquivo .obj
    load_obj()
    # Abre a imagem que será usada como textura
    img = Image.open(sys.argv[2])
    print('opened file: size=', img.size, 'format=', img.format)
    imageData = np.array(list(img.getdata()), np.uint8)

    # Primeira translação para levar o centro do objeto para a origem dos eixos
    # (corrigindo o caso dele ser definido com centro fora da origem)
    T = ut.matTranslate(-obj_center[0], -obj_center[1], -obj_center[2])
    M = np.matmul(T,M)
    # E então corrige a coordenada de centro para o centro após translação
    obj_center[0] -= obj_center[0]
    obj_center[1] -= obj_center[1]
    obj_center[2] -= obj_center[2]

    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertex_array.nbytes, vertex_array, gl.GL_STATIC_DRAW)
    
    # Texture data
    VTO = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, VTO)

    # Texture settings
    for i in range(6):
      gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB, img.size[0], img.size[1], 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, imageData)

    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)  
    
    # Set attributes
    if normal == True:
        # Posição
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertex_array.itemsize, None)
        # Normal
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertex_array.itemsize, c_void_p(3*vertex_array.itemsize))
    else:
        # Posição
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    
    # Unbind Vertex Array Object.
    gl.glEnableVertexAttribArray(0)

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
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Mesh I&T')

    initData()
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutSpecialFunc(special_keyboard)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()