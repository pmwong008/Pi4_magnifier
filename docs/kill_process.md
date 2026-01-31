# Finding orphaned OpenCV process
1. List Python processes: `ps aux | grep python3`
2. Identify the process: Look for one running the program
3. Kill the process: `kill 123456` OR Force kill: `kill -9 123456`