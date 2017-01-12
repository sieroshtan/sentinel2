import re


def params_of_granule(filename, regex_string):
    match = re.search(regex_string, filename)
    if match:
        date_string = match.groupdict().get('date')
        scene_string = match.groupdict().get('scene')
        if date_string and scene_string:
            return date_string, scene_string
    return None, None
