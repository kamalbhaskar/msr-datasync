import logging

def setup_logging():
    logging.basicConfig(filename='execution.log', filemode='w', format='%(asctime)s  %(name)s - %(levelname)s - %(message)s')
    