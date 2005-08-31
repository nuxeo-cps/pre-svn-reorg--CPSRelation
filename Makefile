check:
	pychecker *.py

clean:
	find . -name '*~' | xargs rm -f
	find . -name '*.pyc' | xargs rm -f
	find . -name '#*' | xargs rm -f
encoding:
	find . -name '*.p[y,t]'  | xargs dos2unix -U
	find . -name  '*.csv' | xargs dos2unix -U
doc:
	happydoc -d docs/API *.py
