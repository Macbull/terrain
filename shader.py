'''
Shader: abstract compilation and usage
'''

__all__ = ('ShaderException', 'Shader')

# from pymt.logger import pymt_logger
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, \
        glCreateProgram, glGetUniformLocation, glUniform1i, \
        glUniform1f, glUniformMatrix4fv, glLinkProgram, glCreateShader, glUseProgram, \
        glAttachShader, glCompileShader, glShaderSource, \
        glGetProgramInfoLog, glGetShaderInfoLog,  GL_FALSE, GL_TRUE


class ShaderException(Exception):
    '''Exception launched by shader in error case'''
    pass

class Shader():

    def __init__(self, vertex_source=None, fragment_source=None):
        print("In Shader File")
        self.program = glCreateProgram()
        vertex_file = open(vertex_source, "r")
        fragment_file = open(fragment_source, "r")
        vertex = vertex_file.read()
        fragment = fragment_file.read()
        vertex_file.close()
        fragment_file.close()
        if vertex_source:
            self.vertex_shader = self.create_shader(
                vertex, GL_VERTEX_SHADER)
            glAttachShader(self.program, self.vertex_shader)

        if fragment_source:
            self.fragment_shader = self.create_shader(
                fragment, GL_FRAGMENT_SHADER)
            glAttachShader(self.program, self.fragment_shader)

        glLinkProgram(self.program)
        message = self.get_program_log(self.program)
        if message:
            print('Init Shader: shader program message: %s' % message)

    def create_shader(self, source, shadertype):
        shader = glCreateShader(shadertype)
        # PyOpenGL bug ? He's waiting for a list of string, not a string
        # on some card, it failed :)
        # if isinstance(source, basestring):
        # source = [source]
        glShaderSource(shader, source)
        glCompileShader(shader)
        message = self.get_shader_log(shader)
        if message:
            print(' Create Shader: shader message: %s' % message)
        return shader

    def use(self):
        '''Use the shader'''
        glUseProgram(self.program)

    def stop(self):
        '''Stop using the shader'''
        glUseProgram(0)

    def get_shader_log(self, shader):
        '''Return the shader log'''
        return self.get_log(shader, glGetShaderInfoLog)

    def get_program_log(self, shader):
        '''Return the program log'''
        return self.get_log(shader, glGetProgramInfoLog)

    def get_log(self, obj, func):
        value = func(obj)
        return value
    
    def set_uniform_f(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform1f(location, value)

    def set_uniform_i(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform1i(location, value)

    def setBool(self, name, value): 
        location = glGetUniformLocation(self.program, name)
        glUniform1i(location, value)     

    def setInt(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform1i(location, value) 

    def setUInt(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform1ui(location, value)
        
    def setFloat(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform1f(location, value)

    def setVec2(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform2fv(location, value)
    
    def setVec3(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform3fv(location, value) 

    def setVec4(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform4fv(location, value) 

    def setMat2(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniformMatrix2fv(location, value)

    def setMat3(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniformMatrix3fv(location, value)

    def setMat4(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(location,1, GL_FALSE,  value.data())


    def __setitem__(self, name, value):
        """pass a variable to the shader"""
        if isinstance(value, float):
            self.set_uniform_f(name, value)
        elif isinstance(value, int):
            self.set_uniform_i(name, value)
        else:
            raise TypeError('Only single floats and ints are supported so far')
