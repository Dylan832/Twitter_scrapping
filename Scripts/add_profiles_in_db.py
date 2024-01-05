import sys
from os.path import dirname, realpath
sys.path.insert(0, dirname(dirname(realpath(__file__))))

from Classes.Mysql import Mysql
import json

with open('Ressources/Json/profiles.json', 'r') as f:
    profiles = json.load(f)

for profile in profiles:
    sql="""INSERT INTO profiles (username) VALUES (%s)"""
    params = (profile["username"],)
    Mysql.execute_insert(sql,params=params)
    print(profile["username"])
