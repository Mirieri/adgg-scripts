# GPS Validation Alpha

This code is a Python script for geocoding GPS coordinates in a MySQL database using the Google Maps API, and caching the results to improve performance.

The script first establishes a connection to a MySQL database, selects the rows containing GPS coordinates, and loads cached results from a CSV file if available.

It then defines two functions: check_cache, which checks if a given GPS location is already in the cache, and geocode, which uses the Google Maps API to geocode a GPS location and update the cache.

The script then sets the batch size and number of processes to use for parallel processing, and initializes the processing count. It also defines a callback function to update the processing count after each row is processed.

The script then uses a multiprocessing.Pool to parallelize the processing of the rows in batches. It first applies caching to the batch using check_cache, then applies geocoding to the batch in parallel using pool.map. It updates the cache with any new results, and prints out information about each row as it is processed using print.

Finally, it saves the updated cache to a CSV file.

