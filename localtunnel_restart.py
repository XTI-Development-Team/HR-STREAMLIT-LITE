import subprocess
import time
import os
import signal
import logging
import datetime
import traceback
import re
import threading
import queue

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'localtunnel_{datetime.datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Command to run
CMD = [r"C:\Program Files\nodejs\npx.cmd", "localtunnel", "--port", "8513", "--subdomain", "robustsupportandsolutions"]
ORIGINAL_SUBDOMAIN = "robustsupportandsolutions"  # Store the original subdomain for reference

# Interval in seconds (1 hour)
INTERVAL = 1 * 60 * 60
# Enable console debugging (prints directly to console, bypassing logger)
DEBUG_MODE = True

def reader_thread(pipe, log_level, output_queue):
    """Reads output from a pipe and puts it into a queue."""
    try:
        for line in iter(pipe.readline, ''):
            output_queue.put((log_level, line.strip()))
    except Exception as e:
        logging.error(f"Error in reader thread: {e}")
    finally:
        pipe.close()

def run_localtunnel():
    logging.info("Starting localtunnel...")
    try:
        process = subprocess.Popen(
            CMD,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace',
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )

        if DEBUG_MODE:
            print(f"Debug: Process started with PID {process.pid}")
        logging.info(f"Localtunnel started with PID: {process.pid}")

        # Create a queue to hold the output from the subprocess
        output_queue = queue.Queue()

        # Start threads to read stdout and stderr
        stdout_thread = threading.Thread(target=reader_thread, args=(process.stdout, logging.INFO, output_queue))
        stderr_thread = threading.Thread(target=reader_thread, args=(process.stderr, logging.ERROR, output_queue))
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()

        return process, output_queue
    except Exception as e:
        logging.error(f"Failed to start localtunnel: {str(e)}")
        logging.error(traceback.format_exc())
        return None, None

def stop_localtunnel(process):
    if not process:
        logging.warning("No process to stop")
        return

    if DEBUG_MODE:
        print(f"Debug: Stopping process with PID {process.pid}")
    logging.info(f"Stopping localtunnel (PID: {process.pid})...")

    try:
        # Gracefully terminate the process group
        process.send_signal(signal.CTRL_BREAK_EVENT)
        process.wait(timeout=10)
        logging.info("Localtunnel stopped gracefully.")
    except subprocess.TimeoutExpired:
        logging.warning("Process did not terminate gracefully, forcing termination...")
        process.kill()
        logging.info("Process terminated forcefully.")
    except Exception as e:
        logging.error(f"Error stopping localtunnel: {str(e)}")
        logging.error(traceback.format_exc())
        try:
            process.kill()
        except Exception as kill_e:
            logging.error(f"Failed to kill process after error: {kill_e}")
    finally:
        # Ensure all logs are written
        for handler in logging.getLogger().handlers:
            handler.flush()

def process_logs(output_queue):
    """Processes and logs messages from the output queue."""
    while not output_queue.empty():
        log_level, message = output_queue.get_nowait()
        if message:
            logging.log(log_level, f"Localtunnel: {message}")
            yield message

def main():
    global CMD
    logging.info("=== Localtunnel restart script started ===")
    subdomain_attempts = 0
    max_subdomain_attempts = 10

    while True:
        try:
            # Reset to original subdomain if needed
            if subdomain_attempts > 0 and subdomain_attempts % 3 == 0:
                CMD[CMD.index("--subdomain") + 1] = ORIGINAL_SUBDOMAIN
                logging.info(f"Resetting to original subdomain: {ORIGINAL_SUBDOMAIN}")

            process, output_queue = run_localtunnel()

            if not process:
                logging.warning("Failed to start localtunnel. Retrying in 30 seconds...")
                time.sleep(30)
                continue

            start_time = time.time()
            tunnel_established = False
            tunnel_url = ""

            # Wait for tunnel URL
            while time.time() - start_time < 30 and not tunnel_established: # 30-second timeout
                for output in process_logs(output_queue):
                    if "your url is:" in output.lower():
                        url_match = re.search(r'https://[^\s]+', output.lower())
                        if url_match:
                            tunnel_url = url_match.group(0)
                            if ORIGINAL_SUBDOMAIN in tunnel_url:
                                logging.info(f"Tunnel successfully established with correct URL: {tunnel_url}")
                                tunnel_established = True
                                subdomain_attempts = 0 # Reset on success
                            else:
                                logging.warning(f"Tunnel established but with unexpected URL: {tunnel_url}")
                time.sleep(1)

            if not tunnel_established:
                logging.error("Failed to establish tunnel with the correct URL. Restarting...")
                stop_localtunnel(process)

                # Try a new subdomain
                if subdomain_attempts < max_subdomain_attempts:
                    subdomain_attempts += 1
                    new_subdomain = f"{ORIGINAL_SUBDOMAIN}"
                    CMD[CMD.index("--subdomain") + 1] = new_subdomain
                    logging.info(f"Trying with same subdomain: {new_subdomain}")
                else:
                    logging.warning(f"Max subdomain attempts reached. Resetting to original.")
                    CMD[CMD.index("--subdomain") + 1] = ORIGINAL_SUBDOMAIN
                    subdomain_attempts = 0
                time.sleep(10)
                continue

            logging.info(f"Monitoring tunnel. Next restart in {INTERVAL / 60} minutes.")
            restart_time = datetime.datetime.now() + datetime.timedelta(seconds=INTERVAL)
            logging.info(f"Next scheduled restart at: {restart_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Monitor loop
            while time.time() - start_time < INTERVAL:
                # Log any new output
                for _ in process_logs(output_queue):
                    pass

                # Check if the process has exited
                if process.poll() is not None:
                    logging.warning(f"Localtunnel process exited unexpectedly with code {process.returncode}")
                    break # Exit monitor loop to restart
                time.sleep(5)
            
            # End of interval or unexpected exit
            if process.poll() is None:
                logging.info(f"Scheduled restart interval reached.")
            
            stop_localtunnel(process)
            
            # Log any final output
            for _ in process_logs(output_queue):
                 pass
            logging.info("Localtunnel restart cycle complete.")
            time.sleep(5)

        except KeyboardInterrupt:
            logging.info("Script interrupted by user.")
            if 'process' in locals() and process and process.poll() is None:
                stop_localtunnel(process)
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred in the main loop: {str(e)}")
            logging.error(traceback.format_exc())
            if 'process' in locals() and process and process.poll() is None:
                stop_localtunnel(process)
            time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Fatal error in script: {str(e)}")
        logging.critical(traceback.format_exc())