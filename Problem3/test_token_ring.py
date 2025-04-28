import threading
import queue
import time
import unittest
from unittest.mock import patch, MagicMock
import io
import sys

# Import the RingProcess class from main.py
from main import RingProcess

class TestTokenRing(unittest.TestCase):
    
    def setUp(self):
        # Create queues for communication between processes
        self.q1 = queue.Queue()
        self.q2 = queue.Queue()
        self.q3 = queue.Queue()
        
        # Create ring processes
        self.p1 = RingProcess(1, self.q1, self.q2)
        self.p2 = RingProcess(2, self.q2, self.q3)
        self.p3 = RingProcess(3, self.q3, self.q1)
        
        # Start processes
        for p in (self.p1, self.p2, self.p3):
            p.daemon = True  # Ensure threads terminate with main thread
            p.start()
    
    def tearDown(self):
        # Clean up queues to help garbage collection
        for q in (self.q1, self.q2, self.q3):
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break
    
    def test_token_passing(self):
        """Test that token is correctly passed around the ring."""
        # Capture stdout to verify process output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Initialize the token at process 1
        self.q1.put('TOKEN')
        
        # Give time for the token to travel around the ring at least once
        time.sleep(1.0)
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Check the output
        output = captured_output.getvalue()
        
        # Verify each process received the token at least once
        self.assertIn("Process 1 received TOKEN", output)
        self.assertIn("Process 2 received TOKEN", output)
        self.assertIn("Process 3 received TOKEN", output)
        
        # Verify token passing order
        p1_index = output.find("Process 1 passing TOKEN")
        p2_index = output.find("Process 2 passing TOKEN")
        p3_index = output.find("Process 3 passing TOKEN")
        
        if p1_index != -1 and p2_index != -1:
            self.assertLess(p1_index, p2_index, "Token should pass from P1 to P2")
        if p2_index != -1 and p3_index != -1:
            self.assertLess(p2_index, p3_index, "Token should pass from P2 to P3")
    
    def test_printing_request(self):
        """Test that a process can use the printer when holding the token."""
        # Request printing for process 2
        self.p2.request_printer()
        self.assertTrue(self.p2.requesting)
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Send token to process 1, it should eventually reach process 2
        self.q1.put('TOKEN')
        
        # Wait for token to reach process 2 and printing to complete
        time.sleep(2.0)
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Check output
        output = captured_output.getvalue()
        
        # Process 2 should have received the token
        self.assertIn("Process 2 received TOKEN", output)
        
        # Process 2 should have printed
        self.assertIn("Process 2 is PRINTING", output)
        self.assertIn("Process 2 finished printing", output)
        
        # After printing, the requesting flag should be False
        self.assertFalse(self.p2.requesting)
    
    @patch('random.uniform', return_value=0.1)
    def test_multiple_requests(self, mock_uniform):
        """Test handling of multiple printing requests."""
        # Set all processes to request printing
        for p in (self.p1, self.p2, self.p3):
            p.request_printer()
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Send token to process 1
        self.q1.put('TOKEN')
        
        # Wait for all processes to get a chance to print
        time.sleep(2.0)
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Check output
        output = captured_output.getvalue()
        
        # Each process should print in order as they receive the token
        self.assertIn("Process 1 is PRINTING", output)
        self.assertIn("Process 2 is PRINTING", output)
        self.assertIn("Process 3 is PRINTING", output)
        
        # Verify printing order
        p1_print_index = output.find("Process 1 is PRINTING")
        p2_print_index = output.find("Process 2 is PRINTING")
        p3_print_index = output.find("Process 3 is PRINTING")
        
        self.assertLess(p1_print_index, p2_print_index, "P1 should print before P2")
        self.assertLess(p2_print_index, p3_print_index, "P2 should print before P3")

if __name__ == "__main__":
    unittest.main()