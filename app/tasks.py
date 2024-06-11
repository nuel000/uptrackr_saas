
import subprocess

def run_main_script(email, rss_url):
    subprocess.run(['python', 'main/main.py', email, rss_url])