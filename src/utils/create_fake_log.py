def create_fake_log(with_loops=False):
    artificial_log = []
    if not with_loops:
        for i in range(10):
            artificial_log.append(["a", "b", "c", "g", "e", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "c", "f", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "d", "g", "e", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "d", "e", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "e", "c", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "e", "d", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "c", "b", "e", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "c", "b", "f", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "d", "b", "e", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "d", "b", "f", "g", "h"])
    else:
        for i in range(10):
            artificial_log.append(["a", "b", "c", "c", "e", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "c", "f", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "d", "g", "e", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "d", "e", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "c", "c", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "b", "e", "d", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "c", "b", "e", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "c", "b", "f", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "d", "d", "e", "g", "h"])
        for i in range(10):
            artificial_log.append(["a", "d", "b", "f", "b", "h"])
    return artificial_log
