import json
from rest_framework.parsers import MultiPartParser, DataAndFiles


class MultiPartJSONParser(MultiPartParser):
    """
    Parser for multipart form data that has json.
    """

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(
            stream,
            media_type=media_type,
            parser_context=parser_context,
        )

        data = dict()

        # If a value seems to be a json string, try
        # to parse it accordingly.
        for key, value in result.data.items():
            if not isinstance(value, str):
                data[key] = value
            elif "[" in value or "{" in value:
                try:
                    data[key] = json.loads(value)
                except ValueError:
                    data[key] = value
            else:
                data[key] = value

        return DataAndFiles(data, result.files)
