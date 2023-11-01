from requests import Response
from requests_html import HTMLSession
import json

session = HTMLSession()
r = session.get("http://192.168.1.111")
print(r.status_code)

r.html.render(sleep=1, keep_page=True, scrolldown=1)
data = r.html.find("#func-result-pre")

for item in data:
    data_text = item.text
    data_dict = json.loads(data_text)
    obj = data_dict["obj"]

    for detail in obj:
        print(detail["type"])