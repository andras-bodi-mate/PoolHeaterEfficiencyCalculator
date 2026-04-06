#version 330
#include utilities.glsl

uniform mat4 u_perspectiveProjection;
uniform mat4 u_cameraProjection;
uniform mat4 u_modelTransform;
uniform mat3 u_modelNormalTransform;

in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;
in vec3 in_color;

out vec3 v_position;
out vec3 v_normal;
out vec2 v_uv;
out vec3 v_color;

void main() {
    v_position = in_position;
    v_normal = normalize(u_modelNormalTransform * in_normal);
    v_color = in_color;
    v_uv = in_uv;
    gl_Position = u_perspectiveProjection * u_cameraProjection * u_modelTransform * vec4(in_position, 1.0);
}