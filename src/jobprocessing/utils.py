import yaml

def common_parameters():
    params = yaml.safe_load(open('params.yaml'))
    return params