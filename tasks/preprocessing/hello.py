import requests


class Hello:
    def hello(self, x):
        print("hello %s" % x)
        return x

    def send_hello(self):
        rq = requests.get("http://google.de", {'q': 'hello'})
        return rq.content
