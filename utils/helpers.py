import logging

def setup_logging(log_file='configguard.log'):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('Logging setup complete.')

def read_config(config_file='config/config.yaml'):
    import yaml
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config
