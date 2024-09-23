import os
import yaml
class ConfigHandler:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.config_files = {}
        self.data = {}
    def load_config_files(self):
        for filename in os.listdir(self.config_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                config_file_path = os.path.join(self.config_dir, filename)
                with open(config_file_path, 'r') as file:
                    self.config_files[filename] = yaml.safe_load(file)
    def load_data(self):
        for config_file, data in self.config_files.items():
            self.data.update(data)
    def get_config(self, key):
        return self.data.get(key)
    def set_config(self, key, value):
        self.data[key] = value
        self.save_config_files()
    def save_config_files(self):
        for filename, data in self.config_files.items():
            config_file_path = os.path.join(self.config_dir, filename)
            with open(config_file_path, 'w') as file:
                yaml.dump(data, file, default_flow_style=False)

