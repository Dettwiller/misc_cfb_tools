
def generic_model(home_field_advantage=0.0):
    model = Model(home_field_advantage=home_field_advantage)
    return model

class Model:
    def __init__(self, home_field_advantage=0.0):
        home_field_type_check = isinstance(home_field_advantage, float)
        assert home_field_type_check, "home_field_advantage is not a float: %r" % type(home_field_advantage)
        self.home_field_advantage = home_field_advantage