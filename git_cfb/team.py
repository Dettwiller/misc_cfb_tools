import os

class Team:
    name = ''
    data_dir = os.path.join(os.getcwd(), 'data')
    def __init__(self, name, data_dir=None):
        '''
            TODO: input checking:
                1. name is a string
                    a. have an excel file of all team names and check that it exists
                2. if data_dir is not None, add logic to ensure data_dir:
                    a. is a path
                    b. exists
                    c. create the passed data_dir if it doesn't exist
        '''
        self.name = name
        if data_dir is not None:
            self.data_dir = data_dir

        


