import unittest

if __name__ == '__main__':
    # Define the names of the test files
    test_files = [ 'databaseConnectionTest.py', 'geocodingMechanismTest.py', 'cacheTest.py', 'parallelProcessingTest.py']

    # Create the test suite
    test_suite = unittest.TestSuite()

    # Loop through the test files and add the test cases to the test suite
    for test_file in test_files:
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromName(test_file[:-3]))

    # Run the tests
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
