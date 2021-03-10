# -*- coding: utf-8 -*-
import argparse
import os
import shutil

from github import Github

MD_HEAD = """## ssh 的博客
我的技术博客，不定时更新。

收藏点star，订阅点watch。

博客网站（不定期同步）：https://ssh-blog.vercel.app

Thanks to https://github.com/yihong0618/gitblog
"""

BACKUP_DIR = "src/pages"
ANCHOR_NUMBER = 5
TOP_ISSUES_LABELS = ["Top"]
TODO_ISSUES_LABELS = ["TODO"]


def get_me(user):
    return user.get_user().login


def isMe(issue, me):
    return issue.user.login == me


def format_time(time):
    return str(time)[:10]


def login(token):
    return Github(token)


def get_repo(user: Github, repo: str):
    return user.get_repo(repo)


def parse_TODO(issue):
    body = issue.body.splitlines()
    todo_undone = [l for l in body if l.startswith("- [ ] ")]
    todo_done = [l for l in body if l.startswith("- [x] ")]
    # just add info all done
    if not todo_undone:
        return f"[{issue.title}]({issue.html_url}) all done", []
    return (
        f"[{issue.title}]({issue.html_url})--{len(todo_undone)} jobs to do--{len(todo_done)} jobs done",
        todo_done + todo_undone,
    )


def get_top_issues(repo):
    return repo.get_issues(labels=TOP_ISSUES_LABELS)


def get_todo_issues(repo):
    return repo.get_issues(labels=TODO_ISSUES_LABELS)


def get_repo_labels(repo):
    return [l for l in repo.get_labels()]


def get_issues_from_label(repo, label):
    return repo.get_issues(labels=(label,))


def add_issue_info(issue, md):
    time = format_time(issue.created_at)
    md.write(f"- [{issue.title}]({issue.html_url})--{time}\n")


def add_md_todo(repo, md, me):
    todo_issues = list(get_todo_issues(repo))
    if not TODO_ISSUES_LABELS or not todo_issues:
        return
    with open(md, "a+", encoding="utf-8") as md:
        md.write("## TODO\n")
        for issue in todo_issues:
            if isMe(issue, me):
                todo_title, todo_list = parse_TODO(issue)
                md.write("TODO list from " + todo_title + "\n")
                for t in todo_list:
                    md.write(t + "\n")
                # new line
                md.write("\n")


def add_md_top(repo, md, me):
    top_issues = list(get_top_issues(repo))
    if not TOP_ISSUES_LABELS or not top_issues:
        return
    with open(md, "a+", encoding="utf-8") as md:
        md.write("## 置顶文章\n")
        for issue in top_issues:
            if isMe(issue, me):
                add_issue_info(issue, md)


def add_md_recent(repo, md, me):
    new_last_issues = repo.get_issues()[:10]
    with open(md, "a+", encoding="utf-8") as md:
        # one the issue that only one issue and delete (pyGitHub raise an exception)
        try:
            md.write("## 最近更新\n")
            for issue in new_last_issues:
                if isMe(issue, me):
                    add_issue_info(issue, md)
        except:
            return


def add_md_header(md):
    with open(md, "w", encoding="utf-8") as md:
        md.write(MD_HEAD)


def add_md_label(repo, md, me):
    labels = get_repo_labels(repo)
    with open(md, "a+", encoding="utf-8") as md:
        for label in labels:

            # we don't need add top label again
            if label.name in TOP_ISSUES_LABELS:
                continue

            # we don't need add todo label again
            if label.name in TODO_ISSUES_LABELS:
                continue

            issues = get_issues_from_label(repo, label)
            if issues.totalCount:
                md.write("## " + label.name + "\n")
                issues = sorted(
                    issues, key=lambda x: x.created_at, reverse=True)
            i = 0
            for issue in issues:
                if not issue:
                    continue
                if isMe(issue, me):
                    if i == ANCHOR_NUMBER:
                        md.write("<details><summary>显示更多</summary>\n")
                        md.write("\n")
                    add_issue_info(issue, md)
                    i += 1
            if i > ANCHOR_NUMBER:
                md.write("</details>\n")
                md.write("\n")


def get_to_generate_issues(repo, dir_name, me, issue_number=None):
    to_generate_issues = [
        i
        for i in list(repo.get_issues())
        if isMe(i, me)
    ]
    if issue_number:
        to_generate_issues.append(repo.get_issue(int(issue_number)))
    return to_generate_issues


def main(token, repo_name="blogs", issue_number=None, dir_name=BACKUP_DIR):
    user = login(token)
    me = get_me(user)
    repo = get_repo(user, repo_name)
    add_md_header("README.md")
    # add to readme one by one, change order here
    for func in [add_md_top, add_md_recent, add_md_label, add_md_todo]:
        func(repo, "README.md", me)

    to_generate_issues = get_to_generate_issues(
        repo, dir_name, me, issue_number)
    # save md files to backup folder
    for issue in to_generate_issues:
        save_issue(issue, me, dir_name)


def save_issue(issue, me, dir_name=BACKUP_DIR):
    md_dir = os.path.join(
        dir_name, str(issue.id)
    )
    if not os.path.exists(md_dir):
        os.makedirs(md_dir)
    md_name = os.path.join(md_dir, "index.md")
    with open(md_name, "w") as f:
        f.write('---\n')
        f.write(f"title: '{issue.title}'\n")
        f.write(f"date: '{issue.created_at.strftime('%Y-%m-%d')}'\n")
        f.write("spoiler: ''\n")
        f.write('---\n\n')
        f.write(issue.body)


print(os.path.abspath(BACKUP_DIR))
shutil.rmtree(os.path.abspath(BACKUP_DIR))
os.makedirs(BACKUP_DIR)
parser = argparse.ArgumentParser()
parser.add_argument("github_token", help="github_token")
parser.add_argument("repo_name", help="repo_name")
parser.add_argument("--issue_number", help="issue_number",
                    default=None, required=False)
options = parser.parse_args()
main(options.github_token, options.repo_name, options.issue_number)
