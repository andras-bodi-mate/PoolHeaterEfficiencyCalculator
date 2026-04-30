const float halfPi = 1.57079632679;
const float pi = 3.14159265359;
const float doublePi = 6.28318530718;

float remap(float val, float originalStart, float originalEnd, float newStart, float newEnd) {
    return newStart + (val - originalStart) / (originalEnd - originalStart) * (newEnd - newStart);
}

vec3 rotateVector(vec3 vector, vec4 rotation) {
    vec3 t = 2.0 * cross(rotation.xyz, vector);
    return vector + rotation.w * t + cross(rotation.xyz, t);
}

vec3 sphericalToCartesian(float azimuth, float altitude, float radius) {
    float ca = cos(altitude);

    return vec3(
        radius * ca * cos(azimuth),
        radius * sin(altitude),
        radius * ca * sin(azimuth)
    );
}

float rand(vec2 coord) {
    return fract(sin(dot(coord, vec2(12.9898, 78.233))) * 43758.5453);
}

mat2 rotationMatrix(float angle) {
    return mat2(cos(angle), -sin(angle),
                sin(angle),  cos(angle));
}