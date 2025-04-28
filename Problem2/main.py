import threading
import queue
import time
import random

class RingProcess(threading.Thread):
    def __init__(self, pid, inbox: queue.Queue, next_inbox: queue.Queue):
        super().__init__(daemon=True)
        self.pid = pid
        self.inbox = inbox
        self.next_inbox = next_inbox
        self.requesting = False   

    def request_printer(self):
        self.requesting = True
        print(f"[{time.strftime('%H:%M:%S')}] ▶ Process {self.pid} requested the printer")

    def run(self):

        while True:
            msg = self.inbox.get()  

            if msg == 'TOKEN':
                print(f"[{time.strftime('%H:%M:%S')}] → Process {self.pid} received TOKEN")

                if self.requesting:
                    print(f"[{time.strftime('%H:%M:%S')}] ✱ Process {self.pid} is PRINTING ✱")
                    time.sleep(random.uniform(0.5, 1.0))
                    print(f"[{time.strftime('%H:%M:%S')}] ✔ Process {self.pid} finished printing")
                    self.requesting = False

                time.sleep(0.1) 
                print(f"[{time.strftime('%H:%M:%S')}] → Process {self.pid} passing TOKEN to P{((self.pid)%3)+1}")
                self.next_inbox.put('TOKEN')

def main():
    q1 = queue.Queue()
    q2 = queue.Queue()
    q3 = queue.Queue()

    p1 = RingProcess(1, q1, q2)
    p2 = RingProcess(2, q2, q3)
    p3 = RingProcess(3, q3, q1)

    for p in (p1, p2, p3):
        p.start()

    q1.put('TOKEN')

    def random_requester():
        procs = [p1, p2, p3]
        while True:
            time.sleep(random.uniform(2.0, 5.0))
            proc = random.choice(procs)
            proc.request_printer()

    threading.Thread(target=random_requester, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulation terminated.")

if __name__ == "__main__":
    main()
