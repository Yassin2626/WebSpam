"""
HEY PLEASE READ!!!!
------------------------
Hello! I'm Yassin, a cybersecurity enthusiast and programmer with a passion for ethical hacking and security research.
I'm actively seeking job opportunities in the cybersecurity field. If you have any leads, advice, or opportunities,
please feel free to reach out to me on Discord: yassin1234.
------------------------
Thank you for your support!
"""

import requests  # For sending messages to Discord
import threading # Lets the program do multiple things at once
import sys       # Used to quit the program properly
import time      # Handles waiting and countdowns
from datetime import datetime # Tracks message timestamps
from collections import deque # Keeps track of recent successful messages
from colorama import Fore, Style, init  # Makes terminal text colorful
import os # Clears the screen when starting

# Clears the terminal in the beginning of the script/code
os.system('cls' if os.name == 'nt' else 'clear')


# Initialize colorama
init(autoreset=True)

############################
# Global control variables #
############################
running = True
message_count = 0
success_times = deque()
print_lock = threading.Lock()
counter_lock = threading.Lock()
thread_control_lock = threading.Lock()
original_thread_count = 0
current_thread_count = 0
cooldown_active = False

############################
#          Colors          #
############################
SUCCESS = Fore.GREEN + Style.BRIGHT
ERROR = Fore.RED + Style.BRIGHT
WARNING = Fore.YELLOW + Style.BRIGHT
INPUT = Fore.CYAN + Style.BRIGHT
BANNER_COLOR = Fore.MAGENTA + Style.BRIGHT
RESET = Style.RESET_ALL

# Banner text (Logo)
BANNER = rf"""
{Fore.RED}
 __       __            __         ______
|  \  _  |  \          |  \       /      \
| $$ / \ | $$  ______  | $$____  |  $$$$$$\  ______    ______   ______ ____
| $$/  $\| $$ /      \ | $$    \ | $$___\$$ /      \  |      \ |      \    \ 
| $$  $$$\ $$|  $$$$$$\| $$$$$$$\ \$$    \ |  $$$$$$\  \$$$$$$\| $$$$$$\$$$$\
| $$ $$\$$\$$| $$    $$| $$  | $$ _\$$$$$$\| $$  | $$ /      $$| $$ | $$ | $$
| $$$$  \$$$$| $$$$$$$$| $$__/ $$|  \__| $$| $$__/ $$|  $$$$$$$| $$ | $$ | $$
| $$$    \$$$ \$$     \| $$    $$ \$$    $$| $$    $$ \$$    $$| $$ | $$ | $$
 \$$      \$$  \$$$$$$$ \$$$$$$$   \$$$$$$ | $$$$$$$   \$$$$$$$ \$$  \$$  \$$
                                           | $$                             {Fore.BLUE}v1.0{RESET}{Fore.RED} 
                                           | $$
                                            \$$
{RESET}"""

def print_banner():
    terminal_width = 80
    print(BANNER)
    print(f"{BANNER_COLOR}{'Created by Yassin'.center(terminal_width)}")

def monitor_success_rate():
    global current_thread_count, cooldown_active, original_thread_count
    while running:
        time.sleep(2)  # Check every 2 seconds
        with thread_control_lock:
            # Remove successes older than 3 seconds
            now = datetime.now()
            while success_times and (now - success_times[0]).total_seconds() > 3:
                success_times.popleft()
            
            # Calculate current success rate
            success_rate = len(success_times)
            
            if not cooldown_active:
                if success_rate < current_thread_count * 0.5:
                    # Trigger cooldown
                    new_count = max(1, success_rate)
                    if new_count < current_thread_count:
                        print(f"{WARNING}[*] Adjusting threads from {current_thread_count} to {new_count}{RESET}")
                        current_thread_count = new_count
                        cooldown_active = True
                        threading.Timer(10, reset_thread_count).start()
                elif success_rate > current_thread_count * 1.5:
                    current_thread_count = min(original_thread_count, current_thread_count + 1)

def reset_thread_count():
    global current_thread_count, cooldown_active
    with thread_control_lock:
        current_thread_count = original_thread_count
        cooldown_active = False
        print(f"{WARNING}[*] Resetting to original {original_thread_count} threads{RESET}")

def spam_thread(webhook, message, delay):
    global message_count
    session = requests.Session()
    
    while running:
        try:
            # Check if we should be active
            with thread_control_lock:
                if current_thread_count < original_thread_count and threading.active_count() > current_thread_count + 3:
                    return

            response = session.post(
                webhook,
                json={'content': message},
                timeout=3
            )
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            status = response.status_code

            with counter_lock:
                global message_count
                message_count += 1
                count = message_count

            with print_lock:
                if status == 204:
                    success_times.append(datetime.now())
                    print(f"{Fore.WHITE}{timestamp} {SUCCESS}[SUCCESS]{RESET} Message sent! {Fore.CYAN}[{status}]{RESET} {Fore.MAGENTA}[{count:02d}]{RESET}")
                else:
                    error_msg = f"Webhook error {status}"
                    if status == 429:
                        error_msg += f" (Wait: {response.headers.get('Retry-After', 1)}ms)"
                    print(f"{Fore.WHITE}{timestamp} {ERROR}[ERROR]{RESET} {error_msg} {Fore.MAGENTA}[{count:02d}]{RESET}")

        except Exception as e:
            with counter_lock:
                message_count += 1
                count = message_count
            with print_lock:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{Fore.WHITE}{timestamp} {ERROR}[ERROR]{RESET} Connection failed {Fore.MAGENTA}[{count:02d}]{RESET}")

        time.sleep(delay / 1000)

def start_attack():
    global running, original_thread_count, current_thread_count
    print_banner()

    try:
        # Get delay input
        while True:
            delay_input = input(f"{INPUT}[?] Delay (ms) [1000]: {RESET}")
            if not delay_input:
                delay = 1000.0
                break
            try:
                delay = float(delay_input)
                break
            except ValueError:
                print(f"{ERROR}Please enter a valid number!{RESET}")
        
        # Get webhook URL
        while True:
            webhook = input(f"{INPUT}[?] Webhook URL: {RESET}")
            if webhook.startswith(('http://', 'https://')):
                break
            else:
                print(f"{ERROR}Invalid webhook URL! Please enter a valid URL starting with http:// or https://{RESET}")
        
        # Get message
        message = input(f"{INPUT}[?] Message: {RESET}")
        
        # Get number of threads
        while True:
            number_threads_input = input(f"{INPUT}[?] How many threads: {RESET}")
            try:
                number_threads = int(number_threads_input)
                break
            except ValueError:
                print(f"{ERROR}Please enter a valid number!{RESET}")
        
        original_thread_count = number_threads
        current_thread_count = number_threads

        print(f"\n{WARNING}[*] Starting attack ({delay}ms delay)...{RESET}")
        print(f"{WARNING}[*] Starting attack ({number_threads} Threads)...{RESET}")
        print(f"{WARNING}[*] Press CTRL+C to stop{RESET}")
        print(f"{WARNING}[*] Launching in 3 seconds{RESET}")
        
        for i in range(3, 0, -1):
            print(f"{WARNING}{i}{RESET}")
            time.sleep(1)

        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_success_rate)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Start worker threads
        threads = []
        for _ in range(number_threads):
            t = threading.Thread(target=spam_thread, args=(webhook, message, delay))
            t.daemon = True
            t.start()
            threads.append(t)

        while running:
            time.sleep(0.01)

    except KeyboardInterrupt:
        running = False
        print(f"\n{WARNING}[*] Stopping...{RESET}")
        time.sleep(0.5)
        print(f"{SUCCESS}[+] Attack stopped!{RESET}")
        sys.exit()

if __name__ == "__main__":
    start_attack()
