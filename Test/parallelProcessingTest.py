import multiprocessing as mp
import pandas as pd

from googlemaps.geocoding import geocode


def test_parallel_processing():
    # Define sample data frame
    num_rows = 2000
    df = pd.DataFrame({'id': range(num_rows),
                       'latitude': [i * 0.01 for i in range(num_rows)],
                       'longitude': [i * 0.02 for i in range(num_rows)]})

    # Define batch size and number of processes
    batch_size = 500
    num_processes = 4

    # Run parallel processing
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(geocode, df.to_dict('records'), chunksize=batch_size)

    # Verify number of rows processed
    num_processed = len([r for r in results if r is not None])
    assert num_processed == num_rows
