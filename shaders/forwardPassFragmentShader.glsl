#version 330 core
#include utilities.glsl

uniform vec2 u_sunPosition;
uniform float u_sunlightTransmission;

in vec3 v_position;
in vec3 v_normal;
in vec2 v_uv;
in vec3 v_color;
in vec3 v_fragPos;
in vec4 v_lightSpaceFragPos;

uniform sampler2D s_shadowMap;

layout (location = 0) out vec4 out_color;

const vec3 sunlightColor = vec3(1.0, 0.9, 0.7);

float calculateShadow(vec4 lightSpaceFragPos, vec3 lightDirection) {
    vec3 projCoords = lightSpaceFragPos.xyz / lightSpaceFragPos.w;
    projCoords = projCoords * 0.5 + 0.5;
    float closestDepth = texture(s_shadowMap, projCoords.xy).r;
    float currentDepth = projCoords.z;
    float bias = 0.0005;  
    float shadow = currentDepth - bias > closestDepth  ? 1.0 : 0.0;
    return shadow;
}

void main() {
    vec3 lightDirection = sphericalToCartesian(u_sunPosition.x, u_sunPosition.y, 1.0);

    vec3 ambient = vec3(0.1, 0.1, 0.2);
    vec3 diffuse = sunlightColor * max(dot(v_normal, lightDirection), 0.0) * u_sunlightTransmission;
    float shadow = calculateShadow(v_lightSpaceFragPos, lightDirection);

    vec3 color = (ambient + (1.0 - shadow) * diffuse) * vec3(1.0);

    color += v_normal * 0.000000001 + v_color * 0.000000001 + v_position * 0.000000001 + v_fragPos * 0.000000001 + vec3(v_uv, 0.0) * 0.000000001;
    out_color = vec4(color, 1.0);
}