import re


# from https://stackoverflow.com/q/25121165/5173684
def strip_script_tags(page_source):
    if page_source is None or page_source == '':
        return page_source
    result = page_source
    pattern = re.compile(r'\s?on\w+="[^"]+"\s?')
    result = re.sub(pattern, "", result)
    pattern = re.compile(r"\s?on\w+='[^']+'\s?")
    result = re.sub(pattern, "", result)
    pattern = re.compile(r'<script[\s\S]+?/script>')
    result = re.sub(pattern, "", result)
    return result
