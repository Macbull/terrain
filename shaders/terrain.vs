#version 330

layout (location = 0) in vec3 aPos;

out vec2 texCoords;
uniform mat4 model;
uniform mat4 view;
uniform mat4 perspective;

uniform sampler2D heightMap;

void main()
{
    texCoords = vec2((aPos.x)/2.0 + 0.5, 0.5 -(aPos.z/2.0));

    vec4 Pos = vec4(aPos, 1.0);
    float height = float(texture(heightMap, texCoords));
    Pos.y = height*65535*0.015625*0.125;
    
    gl_Position = perspective * view * model * Pos;
}
