test: lex.py main.py matrix.py mdl.py display.py draw.py gmath.py yacc.py
	python2 main.py no.mdl

clean:
	shred -u *pyc *out parsetab.py

clear:
	shred -u *pyc *out parsetab.py anim/* *.gif
