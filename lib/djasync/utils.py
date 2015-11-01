import shelve


def get_db(path):
    return shelve.open(path)


def get_db_dict(path):
    return dict(get_db(path))
