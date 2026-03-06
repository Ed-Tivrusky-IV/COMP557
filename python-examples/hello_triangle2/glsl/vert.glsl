#version 330

in vec2 in_vert;
in vec3 in_colour;

out vec3 frag_colour;

void main() {
	frag_colour = in_colour;
	gl_Position = vec4(in_vert, 0.0, 1.0);
}