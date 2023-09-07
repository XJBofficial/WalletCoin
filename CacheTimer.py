import requests as Requests
import time as Time



def StartCounting(Seconds : int):
    Time.sleep(Seconds)

    Requests.request(url="http://127.0.0.1:3048/save", method="POST")
    StartCounting(Seconds=Seconds)



if __name__ == "__main__":
    StartCounting(Seconds=10)
