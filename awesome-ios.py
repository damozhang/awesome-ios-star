import os
import re
from urllib.parse import urlparse
import requests
from github import Github
from dotenv import load_dotenv
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

g = Github(ACCESS_TOKEN)

url = "https://raw.githubusercontent.com/vsouza/awesome-ios/master/README.md"
r = requests.get(url)

source = r.text
text = r.text
regex = r"\*\s+(\[.+\])\((https:\/\/[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b[-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)\)(.+)\n"

matches = re.finditer(regex, text, re.MULTILINE)

for matchNum, match in enumerate(matches, start=1):
    url = match.group(2)
    o = urlparse(url)
    if o.hostname != 'github.com':
        continue

    path = o.path.split("/")

    if len(path) < 3:
        continue

    old_line = match.group()
    try:
        full_name = "{}/{}".format(path[1], path[2])
        repo = g.get_repo(full_name)
        star_count = repo.stargazers_count

        new_line = old_line.replace("({})".format(
            url), "({}) [★ {}]".format(url, star_count))
        source = source.replace(old_line, new_line)
        print(new_line)
    except Exception:
        print(old_line)
        continue


f = open("README.md", "w")
f.write(source)
f.close()
