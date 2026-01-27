day05
# python Learning

# 1创建post请求体

import requests

url = "https://httpbin.org/post"
data = {
    "name": "张三",
    "age": 25,
    "skills": ["Python", "Web"]
}

# 使用 json 参数发送
response = requests.post(url, json=data)

print(response.status_code)
print(response.json())  # 查看服务器返回的响应