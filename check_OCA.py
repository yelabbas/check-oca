#!/usr/bin/env python3

import os
import sys
import re
from github import Github
import requests as reqs 

def get_env_var(env_var_name, echo_value=False):
    value=os.environ.get(env_var_name)

    if value is None:
        raise ValueError(f'The environmental variable {env_var_name} is empty!')

    if echo_value:
        print(f"{env_var_name} = {value}")

    return value

def check_oca(github_username):
    print(f"verifying OCA for user : {github_username}")
    pattern = re.compile("^ *$")
    if github_username is None or pattern.match(github_username):
        print("ERROR : github username empty!")
        return False
    requestUrl = "https://oca.opensource.oracle.com/api/v1/members/status?username=" + github_username 
    response = reqs.get(requestUrl) 
    print(response.status_code) 
    if response.status_code == 200:
        return True
    return False

def check_pr(repo,number):
    pr = repo.get_pull(number)
    pr_commits = pr.get_commits()
    pr_mergeable = None
    pr_authors = set()
    pattern = re.compile(".*@oracle.com")

    for commit in pr_commits:
        #print(commit)
        #print(commit.author.id)
        #print(commit.author.login)
        #print(commit.author.email)                
        if (commit.author.email is not None):
            if not (pattern.match(commit.author.email)):
                print(f'pr commit name {commit.sha} author : {commit.author.email}')
                pr_authors.add(commit.author)
        else:
                pr_authors.add(commit.author)

    verified = 0
    for author in pr_authors:
        if not check_oca(commit.author.login):
            print(f'author : {commit.author} (login: "{commit.author.login}") doesn''t have an approved OCA')
            #pr_mergeable = False
        else:
            verified += 1

    if len(pr_authors) > 0 and len(pr_authors) == verified:
        pr_mergeable = True

    return pr_mergeable


def main():
    # Check if the number of input arguments is correct
    if len(sys.argv) != 4:
        raise ValueError('Invalid number of arguments!')

    # Get the GitHub token
    token=sys.argv[1]

    # Get the list of valid labels
    valid_labels=sys.argv[2]
    print(f'Valid labels are: {valid_labels}')

    # Get the PR number
    pr_number_str=sys.argv[3]

    repo_name=get_env_var('GITHUB_REPOSITORY')
    github_ref=get_env_var('GITHUB_REF')
    github_event_name=get_env_var('GITHUB_EVENT_NAME')

    repo = Github(token).get_repo(repo_name)

    if github_event_name == 'pull_request_target':
        try:
            pr_number=int(pr_number_str)
        except ValueError:
            print(f'A valid pull request number input must be defined when triggering on ' \
                f'"pull_request_target". The pull request number passed was "{pr_number_str}".')
            raise
    else:
        try:
            pr_number=int(re.search('refs/pull/([0-9]+)/merge', github_ref).group(1))
        except AttributeError:
            print(f'The pull request number could not be extracted from the GITHUB_REF = ' \
                f'"{github_ref}"')
            raise

    print(f'Pull request number: {pr_number}')

    pr_mergeable = check_pr(repo,pr_number)


    if pr_mergeable:
        exit(0)
    else:
        exit(1)

if __name__ == '__main__':
    main()


