import threading

condition = threading.Condition()

def thread_function():
    with condition:
        print("Thread in attesa...")
        condition.wait()  # Il thread attende fino a quando non viene notificato
        print("Thread ripreso!")

def main():
    thread = threading.Thread(target=thread_function)
    thread.start()

    import time
    time.sleep(2)  # Simula un ritardo

    with condition:
        print("Notifica al thread...")
        condition.notify()  # Notifica al thread in attesa

    thread.join()

if __name__ == "__main__":
    main()