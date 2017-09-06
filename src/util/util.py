import re


def html_to_md(inp):
    out = re.sub(r'<i>|</i>', '_', inp)
    out = re.sub(r'<b>|</b>', '**', out)
    out = re.sub(r'<u>|</u>', '__', out)
    out = re.sub(r'<br>', '\n', out)
    return out
