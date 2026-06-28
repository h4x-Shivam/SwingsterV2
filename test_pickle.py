import time
import pickle

def test_pickle():
    # 1500 symbols, 300 rows each
    data = {}
    for i in range(1500):
        symbol = f"SYMBOL{i}"
        rows = [("2026-06-28", 100.0, 105.0, 95.0, 102.0, 500000) for _ in range(300)]
        data[symbol] = rows
        
    start = time.time()
    pickled = pickle.dumps(data)
    print(f"Pickled in {time.time() - start:.4f} seconds, size: {len(pickled)/1024/1024:.2f} MB")
    
    start = time.time()
    unpickled = pickle.loads(pickled)
    print(f"Unpickled in {time.time() - start:.4f} seconds")

if __name__ == "__main__":
    test_pickle()
