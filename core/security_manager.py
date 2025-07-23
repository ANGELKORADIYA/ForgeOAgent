import os
import time
import threading

class SecurityManager:
    def __init__(self, killswitch_path="../.killswitch", timeout_seconds=10000):
        # Construct the path relative to this script's file location, ensuring it's
        # independent of the current working directory. The final path is resolved
        # to an absolute path for reliability.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.killswitch_path = os.path.abspath(os.path.join(script_dir, killswitch_path))
        self.timeout_seconds = timeout_seconds
        self.start_time = time.time()
        self._stop_event = threading.Event()

    def _terminate_application(self, reason):
        print(f"[SECURITY] Terminating application: {reason}")
        os._exit(1)

    def _check_killswitch_loop(self):
        """Continuously monitor for the killswitch file in the project root or on the Desktop."""
        # Path for killswitch in the project's root directory (from __init__)
        project_killswitch_path = self.killswitch_path

        # Path for killswitch on the user's Desktop, works cross-platform
        killswitch_filename = os.path.basename(project_killswitch_path)
        desktop_killswitch_path = os.path.join(os.path.expanduser("~"), "Desktop", killswitch_filename)

        # Path for killswitch in the temporary directory, OS-specific
        temp_killswitch_path = os.path.join(os.path.abspath("/tmp") if os.name != "nt" else os.path.abspath("C:\\Temp"), killswitch_filename)

        while not self._stop_event.is_set():
            # Check in the project root directory
            if os.path.exists(project_killswitch_path):
                self._terminate_application("Kill switch file detected in project directory.")
                return  # Exit as application is terminating

            # Check on the Desktop as a second location
            if os.path.exists(desktop_killswitch_path):
                self._terminate_application("Kill switch file detected on Desktop.")
                return  # Exit as application is terminating

            # Check in the temporary directory
            if os.path.exists(temp_killswitch_path):
                self._terminate_application("Kill switch file detected in temporary directory.")
                return  # Exit as application is terminating

            time.sleep(1)

    def _enforce_timeout(self):
        """Terminate the app if execution time exceeds the timeout."""
        time_elapsed = time.time() - self.start_time
        remaining = self.timeout_seconds - time_elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._terminate_application("Execution time limit exceeded (2 minutes).")

    def start_monitoring(self):
        """Start both killswitch and timeout monitoring in background threads."""
        # Thread for kill switch
        threading.Thread(target=self._check_killswitch_loop, daemon=True).start()
        # Thread for timeout enforcement
        threading.Thread(target=self._enforce_timeout, daemon=True).start()

    def stop_monitoring(self):
        """Signal the monitoring threads to stop."""
        self._stop_event.set()
