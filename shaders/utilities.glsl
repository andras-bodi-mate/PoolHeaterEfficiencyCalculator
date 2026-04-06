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