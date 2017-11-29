host = 137.165.163.84
port = 8889
run:
	python3 doofus.py $(host)


la:
	python3 doofus.py 127.0.0.1 8825

lb:
	python3 doofus.py 127.0.0.1 8826

