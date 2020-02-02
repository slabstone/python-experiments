import requests
import time
from dataclasses import dataclass

api_version = '5.103'

@dataclass
class OAuthParams:
  """VK OAuth parameters"""

  # registered application id
  client_id: int = 1  # use your client id here

  # default uri
  redirect_uri: str = 'https://oauth.vk.com/blank.html'

  # group ids to get token for (only used for group token)
  group_ids: int = 1

  # display browser authorization page
  display: str = 'page'

  # token access scope
  scope: int = 4096 + 4  # messages + photos

  # default response type
  response_type: str = 'token'

  # revoke previous tokens
  revoke: int = 1

oauth_url = ("https://oauth.vk.com/authorize?"
             "client_id={}&"
             "display={}&"
             "redirect_uri={}&"
             "scope={}&"
             "response_type={}&"
             "v={}")

# base URL for API method invokation
request_url = ("https://api.vk.com/method/{}?"
               "{}&"
               "access_token={}&"
               "v={}")

# paste your access token here
access_token = ''

# chat id offset for group chats
group_offset = 2000000000

message_keys = ['id', 'date', 'peer_id', 'from_id', 'text', 'random_id', 'attachments',
                'important', 'geo', 'payload', 'fwd_messages', 'action',
                # undocumented
                'is_hidden', 'conversation_message_id', 'out',
                # variable
                'update_time']

# https://vk.com/dev/photo_sizes
photo_types = ['s', 'm', 'x', 'o', 'p', 'q', 'r', 'y', 'z', 'w']

def create_oauth_url(params: OAuthParams):
    return oauth_url.format(params.client_id,
                            params.display,
                            params.redirect_uri,
                            params.scope,
                            params.response_type,
                            api_version)

def create_request_url(method, params):
    return request_url.format(method, params, access_token, api_version)

def append_if(str, key, value):
    if key:
        str += '{}={}'.format(key, value)
        
def user_id_to_name(id):
    # TODO
    return id

# message time is represented in epoch time
def epoch_to_local(epoch):
    return time.strftime('%Y.%m.%d %H:%M:%S', time.gmtime(epoch))

# messages api is no longer supported for standalone apps, this function will return nothing
def get_history(peer_id, offset=0, count=20, user_id=None, start_message_id=None,
                rev=0, extended=0, fields=None, group_id=None,
                is_group=False):
    params_string = 'peer_id={}&offset={}&count={}&rev={}&extended={}'
    
    if is_group:
        peer_id += group_offset
    params = params_string.format(peer_id, offset, count, rev, extended)
    
    append_if(params, 'user_id', user_id)
    append_if(params, 'start_message_id', start_message_id)
    append_if(params, 'fields', fields)
    
    r = requests.get(create_request_url('messages.getHistory', params))
    if r.status_code != 200:
        return None

    d = r.json()

    if 'response' in d:
        return d['response']['items']
    elif 'error' in d:
        error = d['error']
        print("could not get history: {} {}".format(error['error_code'], error['error_msg']))
    else:
        print("unknown response {}".format(d))

    return None

def get_more_history(id, messages_per_request, total_requests):
    items = []
    for i in range(total_requests):
        items += get_history(id, count=messages_per_request, offset=i * messages_per_request)
    return items

# generate curl download links for all photos in album
def get_photos(owner_id, album_id):
    url = create_request_url('photos.get',
                             'owner_id={}&album_id={}'.format(owner_id, album_id))
    r = requests.get(url)
    d = r.json()

    for i in d['response']['items']:
        text = i['text']
        text = text.replace('\"', '\'\'')
        text = text.replace('\?', '')

        for s in i['sizes']:
            url = 'curl -RL {} -o "{}-{}.jpg"'.format(s['url'], text, s['type'])
            print(url)

if __name__ == "__main__":
    # legacy messages api code example, will not work
    #messages = get_more_history(user_id, 20, 2)
    #for i in messages:
    #    print("[{}] {}: {}".format(epoch_to_local(i['date']),
    #    user_id_to_name(i['from_id']), i['text']))
    pass
