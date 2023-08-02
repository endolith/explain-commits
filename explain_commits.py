import git


def latest_commit_to_file(repo_path, file_name):
    repo = git.Repo(repo_path)

    # Get the latest commit
    commit = repo.head.commit

    # Get the commit message
    commit_message = commit.message

    # Get the diff, excluding certain file types
    diff = commit.diff('HEAD~1',
                       create_patch=True,
                       ignore_blank_lines=True)

    diff_text = ""
    for d in diff:
        if not d.a_path.endswith(('.hex', '.uvopt')) and not d.diff_binary:
            diff_text += d.diff + "\n"

    # Write to file
    with open(file_name, 'w') as f:
        f.write("Commit Message:\n" + commit_message + "\n")
        f.write("Diff:\n" + diff_text)


# Use the function to write the latest commit to a file
latest_commit_to_file('/path/to/your/repo', 'commit.txt')
