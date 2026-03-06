#version 330

in vec3 frag_colour;
out vec4 color;

void main() {
	color = vec4(frag_colour, 1.0);
}