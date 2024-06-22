import subprocess
import signal

class ProcessManager:
    process = None

    @classmethod
    def start_process(cls, user, rss_user):
        if cls.process is None or cls.process.poll() is not None:
            # No process is running or the existing process has terminated
            script_path = '/home/nuel/uptrackr_saas/main/main.py'
            python_path = '/home/nuel/uptrackr_saas/env/bin/python'
            cls.process = subprocess.Popen([python_path, script_path, rss_user.email, rss_user.rss_url])
            return cls.process.pid
        else:
            # A process is already running
            return None

    @classmethod
    def stop_process(cls):
        if cls.process is not None and cls.process.poll() is None:
            # A process is running, terminate it
            cls.process.send_signal(signal.SIGTERM)
            cls.process.wait()
            cls.process = None
            return True
        else:
            # No process is running
            return False
