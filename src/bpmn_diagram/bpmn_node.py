class BPMNNode:
    def __init__(self, task_name, is_gateway=False, gateway_type=None, is_start=False, is_end=False, is_join=False):
        self.task_name = task_name
        self.is_gateway = is_gateway
        self.gateway_type = gateway_type
        self.is_join = is_join
        self.is_start = is_start
        self.is_end = is_end

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.task_name < other.task_name

    def __eq__(self, other):
        if type(self) is type(other):
            return self.task_name == other.task_name
        else:
            return False

    def __repr__(self):
        return f"{self.task_name}"

    def __key(self):
        return self.task_name
