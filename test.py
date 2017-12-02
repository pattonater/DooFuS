## TEST SUITE FOR DOOFUS
## Ensure that a succuessful test returns 1,
## and an unsuccesful test returns 0
## to use: python3 test.py <test1> <test2> ... <testn>


import sys

def _test_dfs():
    import dfs
    prefix = "DFS TEST: "

    try:
        file_system = dfs.DFS("test_dfs.json")

        if not file_system:
            print(prefix + "ERROR: Failed to create file system instance.")
            print("Ending test.")
            return 0

        print(prefix + "SUCCESS")
        return 1

    except dfs.DFSError as e:
        print(e)
        return 0

if __name__ == "__main__":
    outcome = 0

    for test in sys.argv[1:] :

        if test.lower() == "dfs":
            outcome += _test_dfs()
		
        #elif test.lower() == "othertest":
        #	outcome += _other_test() 

    result = "Success" if outcome == len(sys.argv[1:]) else "Failure"
    print(result + ": passed " + str(outcome) + " of " + str(len(sys.argv[1:])) + " tests.")