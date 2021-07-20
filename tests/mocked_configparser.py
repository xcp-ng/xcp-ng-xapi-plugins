class ConfigParser:
    def __init__(self, dict=None):
        return

    def sections(self):
        return ["repo_yum", "repo_yum_2", "repo_yum_3"]

    def has_section(self, section_name):
        return section_name in self.sections()

    def has_option(self, section_name, field_name):
        try:
            self.read_sections[section_name][field_name]
            return True
        except Exception as e:
            return False

    def get(self, section_name, field_name, default_value=None):
        try:
            section = self.read_sections[section_name]
            field = section[field_name]
            return field
        except Exception as e:
            return default_value

    def set(self, section_name, field_name, value):
        self.read_sections[section_name][field_name] = value

    def read(self, filepath):
        self.read_sections = {
            "repo_yum": {
                "name": "yum_repo",
                "baseurl": "http://yumrepo.example.com/os",
                "enabled": "1",
                "gpgcheck": "0",
                "proxy": "http://user:password@proxy.example.com:3128"
            },
            "repo_yum_2": {
                "name": "yum_repo_2",
                "baseurl": "http://yumrepo.example.com/os",
                "enabled": "1",
                "gpgcheck": "0",
                "proxy": "_none_"
            },
            "repo_yum_3": {
                "name": "yum_repo_3",
                "baseurl": "http://yumrepo.example.com/os",
                "enabled": "1",
                "gpgcheck": "0"
            }
        }
        return [filepath]

    def write(self, file):
        return 0
