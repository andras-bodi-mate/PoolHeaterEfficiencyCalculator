#include utilities.glsl

vec3 colorTemperatureToRgb(float kelvin) {
    float temp = kelvin / 100;
    vec3 color = vec3(0.0);

    if (temp <= 66){ 
        color.r = 255; 
        
        color.g = temp;
        color.g = 99.4708025861 * log(color.g) - 161.1195681661;

        if( temp <= 19){
            color.b = 0;
        }
        else {
            color.b = temp-10;
            color.b = 138.5177312231 * log(color.b) - 305.0447927307;
        }
    }
    else {
        color.r = temp - 60;
        color.r = 329.698727446 * pow(color.r, -0.1332047592);
        
        color.g = temp - 60;
        color.g = 288.1221695283 * pow(color.g, -0.0755148492 );

        color.b = 255;
    }

    return color / 255.0;
}

float colorTempFromAirMass(float airMass) {
    float colorTemp = 2000 + 4500 * exp(-0.15 * (airMass - 1));
    return colorTemp;
}

float getAirMass(float elevation) {
    float zenith = halfPi - elevation;
    float airMass = 1.0 / (cos(zenith) + 0.50572 * pow(96.07995 - zenith * 0.0174533, -1.6361));
    return airMass;
}

vec3 getSunColor(float elevation) {
    float airMass = getAirMass(elevation);
    float colorTemp = colorTempFromAirMass(airMass);
    vec3 sunlightColor = colorTemperatureToRgb(colorTemp);
    return sunlightColor;
}