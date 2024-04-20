import os
import re
import datetime
from urllib.parse import urlparse
import requests
from github import Github
from github import GithubException
from dotenv import load_dotenv
load_dotenv()

start_at = datetime.datetime.now()


def extractList(text):
    result = []

    regex = r".*\s+(\[[^]]+\])\s*\((https:\/\/[github\.com]{1}[^)]+)\)(.+)\n"
    matches = re.finditer(regex, text, re.MULTILINE)

    for matchNum, match in enumerate(matches, start=1):
        url = match.group(2)
        o = urlparse(url)
        if o.hostname != 'github.com':
            continue

        path = o.path.split("/")

        if len(path) < 3:
            continue

        oldLine = match.group()

        fullName = "{}/{}".format(path[1], path[2])

        repo = {
            'full_name': fullName,
            'old_line': oldLine,
            'url': url
        }

        result.append(repo)

    return result


def save(text):
    f = open("README.md", "w")
    f.write(text)
    f.close()


if __name__ == "__main__":
    url = "https://raw.githubusercontent.com/vsouza/awesome-ios/master/README.md"
    r = requests.get(url)
    source = r.text
    text = r.text
    sourceList = extractList(text)
    print("{} repos have been extracted.".format(len(sourceList)))

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    g = Github(ACCESS_TOKEN)

    print("Rate Limit: {}".format(g.get_rate_limit()))

    for row in sourceList:
        try:
            repo = g.get_repo(row['full_name'])
            starCount = repo.stargazers_count

            newLine = row['old_line'].replace(
                "({})".format(row['url']),
                "({}) :star: {}".format(row['url'], starCount)
            )

            source = source.replace(row['old_line'], newLine)
            print(newLine)
        except GithubException as err:
            if err.status == 404:
                newLine = row['old_line'].replace('- [', '- ~~[')
                newLine = "{}~~\n".format(newLine.rstrip())
                source = source.replace(row['old_line'], newLine)
                print(newLine)
                continue
            break
        except Exception as err:
            print("err: {} {}".format(row['old_line'], err))
            # continue
            break

    save(source)

    end_at = datetime.datetime.now()
    print("{} {} update".format(end_at, end_at - start_at))
