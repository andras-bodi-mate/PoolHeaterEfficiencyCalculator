#version 330 core
#include utilities.glsl

uniform mat4 u_projectionTransform;
uniform mat4 u_viewTransform;
uniform mat4 u_modelTransform;
uniform mat3 u_modelNormalTransform;
uniform mat4 u_lightSpaceMatrix;

in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;
in vec3 in_color;

out vec3 v_position;
out vec3 v_normal;
out vec2 v_uv;
out vec3 v_color;
out vec3 v_fragPos;
out vec4 v_lightSpaceFragPos;

void main() {
    v_fragPos = vec3(u_modelTransform * vec4(in_position, 1.0));
    v_position = in_position;
    v_normal = normalize(u_modelNormalTransform * in_normal);
    v_color = in_color;
    v_uv = in_uv;
    v_lightSpaceFragPos = u_lightSpaceMatrix * vec4(v_fragPos, 1.0);
    gl_Position = u_projectionTransform * u_viewTransform * vec4(v_fragPos, 1.0);
}