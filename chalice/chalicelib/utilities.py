import os
import json
import importlib
from datetime import datetime


class Utilities():

    def to_json(self, data, pretty=False):
        if pretty:
            json_data = json.dumps(data, default=self.to_json_type_convert, indent=4, separators=(',', ': '))
        else:
            json_data = json.dumps(data, default=self.to_json_type_convert)
        return json_data

    def to_json_type_convert(self, item):
        if isinstance(item, datetime):
            return item.__str__()

    def get_mime_type(self, file):
        # I've removed the python-magic library because the
        # it fails to be installed in the chalice deploy
        # and returns the wrong type for a number of common types
        file_name, ext = os.path.splitext(file)

        known_types = {
            ".html": "text/html",
            ".js": "text/javascript",
            ".css": "text/css",
            ".svg": "image/svg",
            ".png": "image/png",
            ".jpeg": "image/jpeg",
            ".jpg": "image/jpeg",
            ".ico": "image/x-icon",
            ".woff": "font/woff",
            ".woff2": "font/woff",
            ".eot": "font/eot",
            ".txt": "text/plain",
            ".md": "text/plain"
        }

        default_type = "application/octet-stream"

        if ext in known_types:
            mime_type = known_types[ext]
        else:
            mime_type = default_type

        return mime_type

    # use importlib to create an instance of a class defined
    # as a string in the database
    def get_class_by_name(self, class_path):
        module_name, class_name = class_path.rsplit(".", 1)
        ClientClass = getattr(importlib.import_module(module_name), class_name)

        return ClientClass

    def log_typed_exception(output_to_log, err):
        if type(err).__module__ in ['__main__', 'builtins']:
            error_message = "{}: {}".format(type(err).__name__, err)
        else:
            error_message = "{}.{}: {}".format(type(err).__module__, type(err).__name__, err)
        output_to_log(error_message)