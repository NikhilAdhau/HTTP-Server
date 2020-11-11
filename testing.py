import concurrent.futures
import requests
import time

out = []
CONNECTIONS = 100
TIMEOUT = 5


urls = ['http://127.0.0.1:1300/', 'http://127.0.0.1:1300/wallp.jpg'] * 250

def load_url(url, timeout):
    ans = requests.get(url, timeout=timeout)
    return ans.status_code

count = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
    future_to_url = (executor.submit(load_url, url, TIMEOUT) for url in urls)
    time1 = time.time()
    for future in concurrent.futures.as_completed(future_to_url):
        try:
            data = future.result()
            print (data)
            count += 1
        except Exception as exc:
            data = str(type(exc))
        finally:
            out.append(data)

            print(str(len(out)),end="\r")

    time2 = time.time()

print(f'Took {time2-time1:.2f} s')
print (count)

