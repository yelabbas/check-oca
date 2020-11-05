#!/usr/bin/env python3

import os
import sys
import re
import time
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

# Get needed values from the environmental variables
repo_name=get_env_var('GITHUB_REPOSITORY')
github_ref=get_env_var('GITHUB_REF')
github_event_name=get_env_var('GITHUB_EVENT_NAME')

# Create a repository object, using the GitHub token
repo = Github(token).get_repo(repo_name)

# When this actions runs on a "pull_reques_target" event, the pull request number is not
# available in the environmental variables; in that case it must be defined as an input
# value. Otherwise, we will extract it from the 'GITHUB_REF' variable.
if github_event_name == 'pull_request_target':
    # Verify the passed pull request number
    try:
        pr_number=int(pr_number_str)
    except ValueError:
        print(f'A valid pull request number input must be defined when triggering on ' \
            f'"pull_request_target". The pull request number passed was "{pr_number_str}".')
        raise
else:
    # Try to extract the pull request number from the GitHub reference.
    try:
        pr_number=int(re.search('refs/pull/([0-9]+)/merge', github_ref).group(1))
    except AttributeError:
        print(f'The pull request number could not be extracted from the GITHUB_REF = ' \
            f'"{github_ref}"')
        raise

print(f'Pull request number: {pr_number}')
print(f'github_ref: {github_ref}')


pr = repo.get_pull(pr_number)



pr_labels = pr.get_labels()


pr_reviews = pr.get_reviews()

pr_has_valid_label = None
for label in pr_labels:
    print(f'pr label name {label.name}')
    if label.name in valid_labels:
        pr_has_valid_label = True


while pr.merge_commit_sha is None:
    print(f'waiting 5s to get a merge  commit sha, actual one is: {pr.merge_commit_sha}')
    time.sleep(5)
    pr = repo.get_pull(pr_number)

        

if pr_has_valid_label:
    print(f'Success! This pull request contains the following valid labels: {valid_labels}')
    if github_event_name == 'pull_request_target':
        repo.get_commit(sha=pr.merge_commit_sha).create_status(
           state="success",
           target_url="https://www.application.com",
           description="Label check succeded",
           context="OCA Check")
    else:
        repo.get_commit(sha=pr.head.sha).create_status(
            state="success",
            target_url="https://www.application.com",
            description="Label check succeded",
            context="OCA Check")
    exit(0)
else:
    print(f'Error! This pull request does not contain any of the valid labels: {valid_labels}')
    print(f' This pull request: {pr} {pr.head}')

    if github_event_name == 'pull_request_target':
        repo.get_commit(sha=pr.merge_commit_sha).create_status(
           state="success",
           target_url="https://www.application.com",
           description="Label check succeded",
           context="OCA Check")
    else:
        repo.get_commit(sha=pr.head.sha).create_status(
            state="success",
            target_url="https://www.application.com",
            description="Label check succeded",
            context="OCA Check")
    exit(1)

