from os import getcwd

DEFAULT_PYTHON = f"{getcwd()}/.venv/bin/python"

def generate_cron_job_string(
        cron_schedule: str, 
        script_location: str,
        flags: str, 
        user: str = "ryad_pi", 
        python: str = DEFAULT_PYTHON
    ) -> str:
    return f"{cron_schedule} {user} {python} {script_location} {flags}"

def init_cron_job():
    pass

def create_prayer_call_job():
    pass