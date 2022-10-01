import time
from CCAPI import CCAPI

ccapi = CCAPI()
query = {
    "dept": "SPAN",
    "number": "101"
}
results = ccapi.class_search(query=query)
print(results)
time.sleep(6000)