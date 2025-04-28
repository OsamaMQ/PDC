from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

send_msg = f"Message from process {rank}"

successor = (rank + 1) % size
predecessor = (rank - 1 + size) % size

req = comm.isend(send_msg, dest=successor)
recv_msg = comm.recv(source=predecessor)

# Wait for send to complete
req.wait()

print(f"Process {rank} received: '{recv_msg}'")
