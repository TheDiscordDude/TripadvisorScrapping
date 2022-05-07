import os


def restart_program():
    """
    Restarts the program. Most likely because a StaleElementException
    """
    print("Restarting Program")
    os.system('runme.sh')
