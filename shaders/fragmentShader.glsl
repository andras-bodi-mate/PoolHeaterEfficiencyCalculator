#version 330
#include utilities.glsl

uniform vec2 u_sunPosition;
uniform float u_sunlightTransmission;

in vec3 v_position;
in vec3 v_normal;
in vec2 v_uv;
in vec3 v_color;

layout (location = 0) out vec4 out_color;

void main() {
    vec3 lightDirection = sphericalToCartesian(u_sunPosition.x, u_sunPosition.y, 1.0);
    float illumination = lightDirection.y >= 0 ? dot(v_normal, lightDirection) * u_sunlightTransmission : 0.0;
    vec3 color = vec3(1.0) * clamp(illumination, 0.1, 1.0);
    color += v_normal * 0.000000001 + v_color * 0.000000001 + v_position * 0.000000001 + vec3(v_uv, 0.0) * 0.000000001;
    out_color = vec4(color, 1.0);
}