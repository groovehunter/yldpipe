import pykeepass
import yaml

class KeepassGroupBuilder:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.kp = pykeepass.PyKeePass()
    def build_group_structure(self):
        with open(self.yaml_file, 'r') as f:
            group_structure = yaml.safe_load(f)
        self._build_group_structure_recursive(group_structure, self.kp.root_group)
    def _build_group_structure_recursive(self, group_structure, parent_group):
        for group_name, group_children in group_structure.items():
            group = self.kp.add_group(parent_group, group_name)
            if group_children:
                self._build_group_structure_recursive(group_children, group)

class LegacyToNewDatabaseMigrator:
    def __init__(self, legacy_db, new_db, mapping_file):
        self.legacy_db = legacy_db
        self.new_db = new_db
        self.mapping_file = mapping_file
    def migrate(self):
        with open(self.mapping_file, 'r') as f:
            group_mapping = yaml.safe_load(f)
        for entry in self.legacy_db.entries:
            new_group = self._get_new_group(entry, group_mapping)
            if new_group:
                self._migrate_entry(entry, new_group)
    def _get_new_group(self, entry, group_mapping):
        legacy_group = entry.group
        for legacy_group_path, new_group_path in group_mapping.items():
            if legacy_group_path == legacy_group.path:
                new_group = self.new_db.root_group.find_group_by_path(new_group_path)
                return new_group
        return None
    def _migrate_entry(self, entry, new_group):
        new_entry = self.new_db.add_entry(new_group, entry.title, entry.username, entry.password, entry.url, entry.notes)

class EntryValidator:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
    def validate(self, entry):
        for attr, rules in self.config.items():
            value = getattr(entry, attr)
            for rule in rules:
                if not self._apply_rule(value, rule):
                    return False
        return True
    def _apply_rule(self, value, rule):
        if rule['type'] == 'regex':
            import re
            pattern = re.compile(rule['pattern'])
            if not pattern.match(value):
                return False
        elif rule['type'] == 'length':
            if len(value) < rule['min'] or len(value) > rule['max']:
                return False
        # add more rule types as needed
        return True

class EntryNormalizer:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
    def normalize(self, entry):
        for attr, rules in self.config.items():
            value = getattr(entry, attr)
            for rule in rules:
                if rule['type'] == 'lowercase':
                    value = value.lower()
                elif rule['type'] == 'uppercase':
                    value = value.upper()
                elif rule['type'] == 'trim':
                    value = value.strip()
                # add more rule types as needed
            setattr(entry, attr, value)


