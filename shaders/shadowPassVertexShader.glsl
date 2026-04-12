#version 330 core
#include utilities.glsl

uniform mat4 u_projectionTransform;
uniform mat4 u_viewTransform;
uniform mat4 u_modelTransform;

in vec3 in_position;

void main() {
    gl_Position = u_projectionTransform * u_viewTransform * u_modelTransform * vec4(in_position, 1.0);
}