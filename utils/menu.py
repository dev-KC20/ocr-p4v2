

class Menu:
    def __init__(self, name):

        self._options = {}
        self._name = name

    def add_menu(self, number, description_action):
        self._options[number] = (description_action)

    def items(self):
        return self._options.items()

    def get_name(self):
        return self._name

    def get_action(self, number):
        description, action = self._options[number]
        return action

    def __contains__(self, option):
        return str(option) in self._options
