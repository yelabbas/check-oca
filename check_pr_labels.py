#!/usr/bin/env python3

import os
import sys
import re
from github import Github

def get_env_var(env_var_name, echo_value=False):
    value=os.environ.get(env_var_name)

    if value is None:
        raise ValueError(f'The environmental variable {env_var_name} is empty!')

    if echo_value:
        print(f"{env_var_name} = {value}")

    return value

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


pr = repo.get_pull(pr_number)
pr_labels = pr.get_labels()

pr_has_valid_label = None
for label in pr_labels:
    print(f'pr label name {label.name}')
    if label.name in valid_labels:
        pr_has_valid_label = True

if pr_has_valid_label:
    exit(0)
else:
    exit(1)

