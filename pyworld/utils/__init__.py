import yaml


def auto_representer(cls):
    if issubclass(cls, dict):
        yaml.add_representer(cls, lambda dumper, data: dumper.represent_mapping('tag:yaml.org,2002:map', data))
    elif issubclass(cls, list):
        yaml.add_representer(cls, lambda dumper, data: dumper.represent_sequence('tag:yaml.org,2002:seq', data))
    elif issubclass(cls, set):
        yaml.add_representer(cls, lambda dumper, data: dumper.represent_mapping('tag:yaml.org,2002:set', data))
    return cls
