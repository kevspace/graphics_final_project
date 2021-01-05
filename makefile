test: lex.py main.py matrix.py mdl.py display.py draw.py gmath.py yacc.py
	python2 main.py yes.mdl

clean:
	rm *pyc *out parsetab.py

clear:
	rm *pyc *out parsetab.py anim/* *.gif *.png
