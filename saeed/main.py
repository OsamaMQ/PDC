from mpi4py import MPI

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    message = f"Message from process {rank}"

    successor = (rank + 1) % size
    predecessor = (rank - 1 + size) % size

    # Non-blocking send
    send_request = comm.isend(message, dest=successor)

    # Blocking receive
    received_message = comm.recv(source=predecessor)

    # Ensure the send has completed
    send_request.wait()

    print(f"Process {rank} received: '{received_message}'")

if __name__ == "__main__":
    main()
