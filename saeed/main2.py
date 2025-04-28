import threading
import queue
import time
import random

def create_process(pid, inbox, next_inbox):
    return {
        'pid': pid,
        'inbox': inbox,
        'next_inbox': next_inbox,
        'requesting': False
    }

def request_printer(process):
    process['requesting'] = True
    print(f"[{time.strftime('%H:%M:%S')}] ▶ Process {process['pid']} requested the printer")

def process_behavior(process):
    while True:
        msg = process['inbox'].get()

        if msg == 'TOKEN':
            print(f"[{time.strftime('%H:%M:%S')}] → Process {process['pid']} received TOKEN")

            if process['requesting']:
                print(f"[{time.strftime('%H:%M:%S')}] ✱ Process {process['pid']} is PRINTING ✱")
                time.sleep(random.uniform(0.5, 1.0))
                print(f"[{time.strftime('%H:%M:%S')}] ✔ Process {process['pid']} finished printing")
                process['requesting'] = False

            time.sleep(0.1)
            next_pid = (process['pid'] % 3) + 1
            print(f"[{time.strftime('%H:%M:%S')}] → Process {process['pid']} passing TOKEN to P{next_pid}")
            process['next_inbox'].put('TOKEN')

def random_requester(processes):
    while True:
        time.sleep(random.uniform(2.0, 5.0))
        proc = random.choice(processes)
        request_printer(proc)

def main():
    # Create message queues
    q1, q2, q3 = queue.Queue(), queue.Queue(), queue.Queue()

    # Create processes (as dicts)
    p1 = create_process(1, q1, q2)
    p2 = create_process(2, q2, q3)
    p3 = create_process(3, q3, q1)

    processes = [p1, p2, p3]

    # Start process behaviors
    for p in processes:
        threading.Thread(target=process_behavior, args=(p,), daemon=True).start()

    # Initially give the token to process 1
    q1.put('TOKEN')

    # Start random requester
    threading.Thread(target=random_requester, args=(processes,), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulation terminated.")

if __name__ == "__main__":
    main()
