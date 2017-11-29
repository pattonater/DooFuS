host = 137.165.163.84 # change to your ip
port = 8889

# run with just a host, adding a port puts in testing mode for now
run:
	python3 doofus.py $(host)


# run these concurrently for local testing. Dont change the ports
la:
	python3 doofus.py 127.0.0.1 8825
lb:
	python3 doofus.py 127.0.0.1 8826

