import requests
import random
import string
import ctypes
from colorama import Fore, Style, init
from datetime import datetime
import threading
import re

init(autoreset=True)

successful_gens = 0

def __string__(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def __password__():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = "!@#$%^&*()"
    password = ''.join(random.choice(letters) for _ in range(6)) + \
               ''.join(random.choice(digits) for _ in range(2)) + \
               random.choice(special_chars)
    return ''.join(random.sample(password, len(password)))

def __proxies__():
    with open('proxies.txt', 'r') as file:
        proxies = [line.strip() for line in file.readlines()]
    return proxies

def __get_proxy_dict__(proxy):
    ip_port_pattern = re.compile(r'^[\d\.]+:\d+$')
    ip_port_user_pass_pattern = re.compile(r'^[\d\.]+:\d+:[^:]+:[^:]+$')
    
    if ip_port_pattern.match(proxy):
        ip, port = proxy.split(':')
        return {
            "http": f"http://{ip}:{port}",
            "https": f"http://{ip}:{port}"
        }
    elif ip_port_user_pass_pattern.match(proxy):
        ip, port, username, password = proxy.split(':')
        return {
            "http": f"http://{username}:{password}@{ip}:{port}",
            "https": f"http://{username}:{password}@{ip}:{port}"
        }
    else:
        raise ValueError("Proxy format is incorrect. Use ip:port or ip:port:username:password")

def __signup__(use_proxies, proxies):
    global successful_gens
    email = __string__(7) + "@outlook.com"
    password = __password__()

    url_signup = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyAkBGn9sKEUBSMQ9CTFyHHxXas0tdcpts8"

    headers_signup = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "nl,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "content-type": "application/json",
        "origin": "https://www.crazygames.com",
        "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        "x-client-version": "Chrome/JsCore/10.11.1/FirebaseCore-web",
        "x-firebase-gmpid": "",
        "x-firebase-locale": "en"
    }

    payload_signup = {
        "clientType": "CLIENT_TYPE_WEB",
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    if use_proxies:
        proxy = random.choice(proxies)
        proxies_dict = __get_proxy_dict__(proxy)
        response = requests.post(url_signup, headers=headers_signup, json=payload_signup, proxies=proxies_dict)
    else:
        response = requests.post(url_signup, headers=headers_signup, json=payload_signup)

    data = response.json()

    if response.status_code == 200:
        id_token = data.get('idToken')
        current_time = datetime.now().strftime(Fore.BLUE + "%H:%M:%S")
        print(Fore.YELLOW + f"[*] (solved) " + Fore.LIGHTMAGENTA_EX + f"({id_token})")
        print(Fore.CYAN + f"[+] (created) " + Fore.LIGHTMAGENTA_EX + f"({email}:{password})")

        with open('acc.txt', 'a') as acc_file:
            acc_file.write(f"{email}:{password}\n")

        with open('token.txt', 'a') as token_file:
            token_file.write(f"{id_token}\n")

        successful_gens += 1
        ctypes.windll.kernel32.SetConsoleTitleW(f"solved: {successful_gens} created {successful_gens}")

        return True
    else:
        print(Fore.RED + "Signup failed!")
        print(Fore.RED + f"Error: {data.get('error', {}).get('message', 'Unknown error')}")
        return False

def __main__():
    num_threads = int(input(Fore.CYAN + "Enter the number of threads: "))
    total_accounts = int(input(Fore.CYAN + "Enter the total number of accounts to generate: "))
    use_proxies = input(Fore.CYAN + "Use proxies? (y/n): ").lower() == 'y'
    proxies = __proxies__() if use_proxies else []

    def __worker__(accounts_to_create):
        for _ in range(accounts_to_create):
            __signup__(use_proxies, proxies)
        print(f"Thread completed with {successful_gens} successful generations.")

    threads = []
    accounts_per_thread = total_accounts // num_threads
    extra_accounts = total_accounts % num_threads

    for i in range(num_threads):
        if i < extra_accounts:
            thread = threading.Thread(target=__worker__, args=(accounts_per_thread + 1,))
        else:
            thread = threading.Thread(target=__worker__, args=(accounts_per_thread,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(Fore.GREEN + f"Total successful generations: {successful_gens}")
    print(f"\033]0;genned [{successful_gens}]\007")

if __name__ == "__main__":
    __main__()
