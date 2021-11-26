import os

env = os.environ.get('KIWI_API_KEY')
if env is None:
    print("Count not read KIWI_API_KEY")

print("env var is probably hidden!")    
print(env)

from dotenv import load_dotenv
load_dotenv()
second_time_env = os.environ['KIWI_API_KEY']
if second_time_env is None:
    print("Count not read KIWI_API_KEY by os.environ")

print("second_time_env var is probably hidden!")
print(second_time_env)