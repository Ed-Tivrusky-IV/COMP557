#version 330 core

uniform vec3 colour;
in vec3 v_norm;

out vec4 f_color;
void main() {
	vec3 l = normalize(vec3(10, 10, 25));
	vec3 n = normalize(v_norm);
	float lum = max(dot(n,l),0) + 0.1;
	// Add a bit of specular using half angle	
	vec3 h = normalize(n+l);
	float spec = pow(max(dot(h,n),0),64.0);
	f_color = vec4(colour*lum + vec3(1,1,1)*spec, 1.0);
}

