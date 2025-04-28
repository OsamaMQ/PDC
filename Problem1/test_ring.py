from mpi4py import MPI
import sys

def test_ring_communication():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    # Test requires at least 2 processes
    if size < 2:
        if rank == 0:
            print("Error: This test requires at least 2 processes.")
            print("Use: mpiexec -n <num_processes> python test_ring.py where <num_processes> >= 2")
        return False

    # Generate unique test messages for verification
    test_message = f"Test message from {rank}"
    
    # Calculate ring topology
    successor = (rank + 1) % size
    predecessor = (rank - 1 + size) % size

    # Send message to next process in ring
    req = comm.isend(test_message, dest=successor)
    
    # Receive message from previous process in ring
    received_msg = comm.recv(source=predecessor)
    
    # Wait for non-blocking send to complete
    req.wait()
    
    # Verify message is from the expected source
    expected_source = predecessor
    message_parts = received_msg.split()
    actual_source = int(message_parts[-1])
    
    if actual_source != expected_source:
        print(f"Error in Process {rank}: Expected message from {expected_source}, but message appears to be from {actual_source}")
        return False
    
    print(f"Process {rank} test passed! Received '{received_msg}'")
    
    # Collective verification that all processes passed their tests
    all_passed = comm.allreduce(True, op=MPI.LAND)
    
    if rank == 0 and all_passed:
        print("\n[SUCCESS] All tests passed! Ring communication is working correctly.")
    elif rank == 0:
        print("\n[FAILED] Test failed: At least one process reported an error.")
    
    return all_passed

if __name__ == "__main__":
    success = test_ring_communication()
    if not success:
        sys.exit(1)  # Exit with error code if test failed