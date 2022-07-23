import requests
import json

def get_file_list(srnumber):
    a = requests.session()
    s = a.get('https://scripts.cisco.com/api/v2/auth/login',
              headers={
                  'authorization': 'Basic '
              })

    s = a.get(f'https://scripts.cisco.com/api/v2/attachments/{srnumber}')
    print(s.status_code)
    if s.status_code==404:
        return False
    return json.loads(s.content.decode())


if __name__ == '__main__':
    print(get_file_list(691346159))
