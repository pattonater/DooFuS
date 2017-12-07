port = 8889

# run with just a host, adding a port puts in testing mode for now
run:
	python3 doofus.py hugo

ryan:
	python3 doofus.py ryan

marc:
	python3 doofus.py marc


# run these concurrently for local testing. Dont change the ports
la:
	python3 doofus.py hugo 8825
lb:
	python3 doofus.py hugo 8826

# add test modules after 'dfs' as they are impelemented
test: 
	python3 test.py dfs
