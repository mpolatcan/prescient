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

import yaml


class PrescientConfig:
    def __init__(self, config_filename):
        # Load config from file
        with open(config_filename, "r") as stream:
            try:
                self.config = yaml.load(stream)
            except yaml.YAMLError as ex:
                print(ex)

    # -------------------------- FOR REQUIRED ATTRIBUTES --------------------------------
    def get_bool(self, attr_str):
        try:
            return str(self.config[attr_str]).lower() in ("true", "True")
        except KeyError:
            raise KeyError("There is no attribute with name \"" + attr_str + "\"")

    def get_str(self, attr_str):
        try:
            return str(self.config[attr_str])
        except KeyError:
            raise KeyError("There is no attribute with name \"" + attr_str + "\"")

    def get_int(self, attr_str):
        try:
            return int(self.config[attr_str])
        except KeyError:
            raise KeyError("There is no attribute with name \"" + attr_str + "\"")

    def get_float(self, attr_str):
        try:
            return float(self.config[attr_str])
        except KeyError:
            raise KeyError("There is no attribute with name \"" + attr_str + "\"")
    # ---------------------------------------------------------------------------------

    # ------------------------- FOR OPTIONAL ATTRIBUTES -----------------------------------
    def get_list(self, attr_str):
        try:
            return self.config[attr_str]
        except KeyError:
            return None
