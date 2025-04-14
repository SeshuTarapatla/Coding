from pprint import pprint
from my_modules import kubernetes


data = kubernetes.get_json("postgres-auth-secret", "secret", base64decode=True)
pprint(data)
