from stem import process  # launch_tor
import requests  # also requires 'pysocks' for socks5 proxy

# сайт для проверки IP-адреса
ip_check_url = 'https://httpbin.org/ip'

# реальный IP-адрес
real_ip = '127.0.0.1'

# 'tor.exe' proxies
tor_app_proxies = {'http':  'socks5://127.0.0.1:9050',
                   'https': 'socks5://127.0.0.1:9050'}

# 'Tor Browser' proxies
tor_browser_proxies = {'http':  'socks5://127.0.0.1:9150',
                       'https': 'socks5://127.0.0.1:9150'}

# proxies used by 'requests'
req_proxies = tor_app_proxies

class TorError(Exception):
    pass

# вспомогательный класс для обертки операций в tor
class TorLauncher:
    def __init__(self, launch, real_ip):
        self.launch = launch
        self.real_ip = real_ip
        
    # on 'with'
    def __enter__(self):
        if self.launch:
            print("Launching Tor ...")
            self.tor = process.launch_tor()
        else:
            print("Skipping Tor launch...")
            self.tor = None
        
        # проверка IP-адреса
        try:
            data = requests.get(ip_check_url, proxies=req_proxies)
        except Exception as e:
            print(e)
            return False

        exit_ip = (data.json())["origin"]
        if exit_ip == self.real_ip:
            print("Tor failed, IP exposed!")
            return False
        else:
            print("Tor OK %s" % exit_ip)
            return True
    
    def __exit__(self, type, value, traceback):
        if self.tor:
            print("Terminating Tor ...")
            self.tor.terminate()

if __name__ == "__main__":
    with TorLauncher(True, real_ip) as tor:
        pass