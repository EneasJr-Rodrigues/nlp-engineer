import json
import yaml
from utils import logger


class Convert:
    def __init__(self):
      self.data_type =[]


    @classmethod
    def convert_json_to_yml(self, json_string):
       
        logger.info("Start Process to Convert JSON from YAML")
        logger.info(f'data format is: \n {json_string}')
        python_dict=json.loads(json_string)
        ymal_string=yaml.dump(python_dict)
        logger.info(f'format return: \n {ymal_string}')

        logger.info("Start Process to Convert YAML from DataFrame")

        return ymal_string
    