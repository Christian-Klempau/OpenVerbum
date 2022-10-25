import queue
from command_runner import command_runner_threaded

output_queue = queue.Queue()
stream_output = ""
thread_result = command_runner_threaded(
    "python backend/processor.py video.mp4 video", shell=True, method="poller", stdout=output_queue
)

read_queue = True
while read_queue:
    try:
        line = output_queue.get(timeout=0.1)
    except queue.Empty:
        pass
    else:
        if line is None:
            read_queue = False
        else:
            print(line)
            stream_output += line
            # ADD YOUR LIVE CODE HERE

# Now we may get exit_code and output since result has become available at this point
exit_code, output = thread_result.result()
