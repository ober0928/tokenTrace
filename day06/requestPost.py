import requests

url = "https://mainnet.helius-rpc.com/?api-key=91f4f4c1-d900-47de-bf2b-4c677832f0ab"
data = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getAccountInfo",
    "params": [
        "G5KeBuoDtmBrRQt9fMy29FCUSXDWMwHe7W4skfwDtURv",
        {
            "encoding": "base58"
        }
    ]
}

# 使用 json 参数发送
response = requests.post(url, json=data)

print(response.status_code)
print(response.json())  # 查看服务器返回的响应