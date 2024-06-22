import subprocess
import signal

class ProcessManager:
    processes = {}  # Dictionary to store user -> process mapping

    @classmethod
    def start_process(cls, user, rss_user):
        if user.username not in cls.processes or cls.processes[user.username].poll() is not None:
            # No process is running for the user or the existing process has terminated
            script_path = '/home/nuel/uptrackr_saas/main/main.py'
            python_path = '/home/nuel/uptrackr_saas/env/bin/python'
            process = subprocess.Popen([python_path, script_path, rss_user.email, rss_user.rss_url])
            cls.processes[user.username] = process
            return process.pid
        else:
            # A process is already running for the user
            return None


    @classmethod
    def stop_process(cls, user):
        if user.username in cls.processes and cls.processes[user.username].poll() is None:
            # A process is running for the user, terminate it
            try:
                cls.processes[user.username].send_signal(signal.SIGTERM)
                cls.processes[user.username].wait(timeout=5)  # Timeout in seconds
                del cls.processes[user.username]
                return True
            except subprocess.TimeoutExpired:
                # If the process doesn't stop within the timeout, use SIGKILL
                cls.processes[user.username].send_signal(signal.SIGKILL)
                cls.processes[user.username].wait()
                del cls.processes[user.username]
                return True
            except Exception as e:
                print(f"Error stopping process for user {user.username}: {e}")
                return False
        else:
            # No process is running for the user
            return False

    # @classmethod
    # def stop_process(cls, user):
    #     if user.username in cls.processes and cls.processes[user.username].poll() is None:
    #         # A process is running for the user, terminate it
    #         cls.processes[user.username].send_signal(signal.SIGTERM)
    #         cls.processes[user.username].wait()
    #         del cls.processes[user.username]
    #         return True
    #     else:
    #         # No process is running for the user
    #         return False
