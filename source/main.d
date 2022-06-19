module main;

extern(C): // disable D mangling

double add(double a, double b) { return a + b; }

version(WebAssembly)

	void _start() {}

else

	void main() {}
