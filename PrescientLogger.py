'''
      _______  _______    _______    _______   ________  ___  _______  __      __  ___________
    /   __  / /  ___  \  /  ____/  /  _____/ /  ______\ /  / /  ____/ /  \   / / /____  _____/
   /  /__/ / /  |__|  | /  /___   /  /____  /  /       /  / /  /___  /   \  / /     /  /
  / ______/ / __  ___/ /  ____/  /______ / /  /       /  / /  ____/ /  /\ \/ /     /  /
 / /       / /  \ \   / /____  _______/ / /  /_____  /  / /  /___  /  / \   /     /  /
/_/       /_/    \_\ /______/ /________/ /________/ /__/ /______/ /__/  \__/     /__/

Created by Mutlu Polatcan
01.02.2018
'''

import threading
from colorama import Style, init, deinit
semaphore = threading.BoundedSemaphore(value=1)


class PrescientLogger:
    def __init__(self):
        pass

    @staticmethod
    def console_log(owner, color, *logs):
        semaphore.acquire()

        init()

        for log in logs:
            if owner:
                print(Style.BRIGHT + color + "[" + owner + "] -> " + log + "\n" + Style.RESET_ALL)
            else:
                print(Style.BRIGHT + color + log + Style.RESET_ALL)

        deinit()

        semaphore.release()
