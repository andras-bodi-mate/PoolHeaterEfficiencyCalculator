#version 330 core
#include utilities.glsl

uniform mat4 u_perspectiveProjection;
uniform mat4 u_cameraProjection;
uniform mat4 u_modelTransform;

in vec3 in_position;

void main() {
    gl_Position = u_perspectiveProjection * u_cameraProjection * u_modelTransform * vec4(in_position, 1.0);
}