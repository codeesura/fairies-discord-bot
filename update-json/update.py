import requests
import json

data_list = []

for i in range(1, 1001):
    url = f'https://api.starkscan.co/api/v0/nft/0x01bd387d18e52e0a04a87c5f9232e9b3cbd1d630837926e6fece2dea4a65bea9/{i}'
    headers = {
        "accept": "application/json",
        "x-api-key": "YOUR_API_KEY"
    }
    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        data = response.json()
        data_list.append(data)

with open('fairieswalet.json', 'w') as outfile:
    json.dump(data_list, outfile,indent=4)
