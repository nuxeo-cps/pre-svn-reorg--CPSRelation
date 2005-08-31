check:
	pychecker2 *.py

clean:
	find . "(" -name "*~" -or  -name ".#*" -or -name "*.pyc" ")" -print0 | xargs -0 rm -f
encoding:
	find . -name '*.p[y,t]'  | xargs dos2unix -U
	find . -name  '*.csv' | xargs dos2unix -U
doc:
	happydoc -d docs/API *.py
