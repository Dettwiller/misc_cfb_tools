import os

def team(name, data_dir=os.getcwd()):
    team_ = Team(name, data_dir=data_dir)
    return team_

class Team:
    def __init__(self, name, data_dir=os.getcwd()):
        name_type_check = isinstance(name, str)
        assert name_type_check, "name is not a string: %r" % type(name)
        data_dir_file_check = os.path.isfile(data_dir)
        data_dir_exist_check = os.path.exists(data_dir)
        data_dir_error_statement = "data_dir must be existing directory: %r" % data_dir
        assert data_dir_exist_check and not data_dir_file_check, data_dir_error_statement

        self.name = name
        self.data_dir = data_dir

    def get_drive_data(self):
        pass