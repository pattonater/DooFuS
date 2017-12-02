## TEST SUITE FOR DOOFUS
## Ensure that a succuessful test returns 1,
## and an unsuccesful test returns 0
## to use: python3 test.py <test1> <test2> ... <testn>

import sys
import traceback

def _test_dfs():
    import dfs
    prefix = "DFS TEST: "

    try:
        file_system = dfs.DFS("test_dfs.json")

        if not file_system:
            print(prefix + "ERROR: Failed to create file system instance.")
            print("Ending test.")
            return 0

        # Remove and add file to DFS
        file_system.delete_file("newfile")
        file_system.add_file("newfile", "userA")

        # Test exception-throwing
        try:
            file_system.delete_file("fakefile")
            print(prefix + "ERROR: was able to \"remove\" nonexistent file.")
            return 0
        except dfs.DFSRemoveFileError:
            pass 

        try:
            file_system.add_file("newfile", "userA")
            print(prefix + "ERROR: was able to add the same file twice.")
            return 0
        except dfs.DFSAddFileError:
            pass

    except dfs.DFSError as e:
        print(prefix)
        print traceback.print_tb(e.__traceback__)
        return 0
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        return 0

    print(prefix + "SUCCESS")
    return 1


if __name__ == "__main__":
    outcome = 0

    for test in sys.argv[1:] :

        if test.lower() == "dfs":
            outcome += _test_dfs()
		
        #elif test.lower() == "othertest":
        #	outcome += _other_test() 

    result = "Success" if outcome == len(sys.argv[1:]) else "Failure"
    print(result + ": passed " + str(outcome) + " of " + str(len(sys.argv[1:])) + " tests.")
