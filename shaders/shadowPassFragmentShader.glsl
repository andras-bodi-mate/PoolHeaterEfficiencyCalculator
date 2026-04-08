#version 330 core
#include utilities.glsl

uniform uint u_objectId;

layout (location = 0) out uint out_color;

void main() {
    out_color = u_objectId;
}