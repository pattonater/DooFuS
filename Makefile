port = 8889

# run with just a host, adding a port puts in testing mode for now
run:
	python3 doofus.py


# run these concurrently for local testing. Dont change the ports
la:
	python3 doofus.py 8825
lb:
	python3 doofus.py 8826

