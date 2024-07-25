class Navigation:
    def __init__(self, data_analysis):
        self.data_analysis = data_analysis

    def get_directions_for_visitor(self, current_location, destination):
        return self.data_analysis.get_directions(current_location, destination)
