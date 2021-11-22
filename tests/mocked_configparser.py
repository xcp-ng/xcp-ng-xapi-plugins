class ConfigParser(object):
    def __init__(self, defaults={}):
        self._defaults = defaults
        self._sections = {}

    def sections(self):
        raise Exception('Mock me!')

    def read(self, filepath):
        raise Exception('Mock me!')

    def write(self, filepath):
        raise Exception('Mock me!')

    def has_section(self, section_name):
        return section_name in self.sections()

    def has_option(self, section_name, field_name):
        try:
            self._sections[section_name][field_name]
            return True
        except Exception:
            return False

    def get(self, section_name, field_name, default_value=None):
        try:
            section = self._sections[section_name]
            field = section[field_name]
            return field
        except Exception:
            return default_value

    def set(self, section_name, field_name, value):
        self._sections[section_name][field_name] = value
