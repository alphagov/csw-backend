import sys
import os
import json
import traceback
import importlib
from datetime import datetime, date


class Utilities:
    def to_json(self, data, pretty=False):
        if pretty:
            json_data = json.dumps(
                data,
                default=self.to_json_type_convert,
                indent=4,
                separators=(",", ": "),
            )
        else:
            json_data = json.dumps(data, default=self.to_json_type_convert)
        return json_data

    def to_json_type_convert(self, item):
        if isinstance(item, datetime):
            return item.__str__()
        elif isinstance(item, date):
            return item.__str__()

    def from_json(self, json_data):
        data = json.loads(json_data)
        return data

    def read_file(self, path, binary=False):
        mode = 'rb' if binary else 'r'
        with open(path, mode) as file:
            data = file.read()
            file.close()
        return data

    def write_file(self, path, data, binary=False):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        mode = 'wb' if binary else 'w'
        with open(path, mode) as file:
            file.write(data)
            file.close()

    def parse_datetime(self, date_string):
        date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        return date_object

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
            ".md": "text/plain",
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

    def get_typed_exception(self):
        """Finds the current exception and returns a JSON formatted
        representation. Useful when outputting stack traces to
        cloudwatch.

        """
        return json.dumps({
            "message": traceback.format_exc().split("\n"),
            "stack": [
                {
                    "filename": frame.filename,
                    "line": frame.line,
                    "lineno": frame.lineno,
                    "locals": frame.locals,
                    "name": frame.name,
                }
                for frame in traceback.extract_tb(sys.exc_info()[2])
            ]
        })

    def list_files_from_path(self, path, ext=None):
        """
        Get a list of items in the directory represented by the relative path `path`, only returning files that end
        with ".{ext}", while excluding hidden files.

        The list will contain strings that represent relative paths to the files.
        """
        abs_path = os.path.join(os.getcwd(), path)

        items = []
        for item in os.listdir(abs_path):
            is_required_ext = ext is None or item.endswith(f".{ext}")
            is_hidden = item.startswith(".")
            if is_required_ext and not is_hidden:
                items.append(os.path.join(path, item))

        return items
