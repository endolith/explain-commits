import argparse
import os

import git


def commit_to_file(repo_path, commit_hash=None, include_extensions=None):
    repo = git.Repo(repo_path)

    # Get the specified commit, or default to the latest commit
    commit = repo.commit(commit_hash) if commit_hash else repo.head.commit

    # Get the diff
    parent = commit.parents[0] if commit.parents else None
    diff = parent.diff(commit, create_patch=True) if parent else None

    diff_text = ""
    if diff:
        for d in diff.iter_change_type('M'):
            if (include_extensions is None or
                    d.a_path.endswith(include_extensions)):
                diff_text += d.__str__()

    # Define output file name
    output_file = os.path.join(repo_path, f"{commit.hexsha}.txt")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Commit Message:\n" + commit.message + "\n")
        if diff_text:
            f.write("Diff:\n" + diff_text)

    print(f"Commit information written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Write commit info to a file.")
    parser.add_argument("path", help="Path to the git repository.")
    parser.add_argument("-c", "--commit",
                        help="Specific commit hash. If not specified, "
                        "defaults to the latest commit.")
    parser.add_argument("-i", "--include",
                        help="Comma-separated list of file extensions to "
                        "include. Defaults to .c,.h",
                        default=".c,.h")

    args = parser.parse_args()
    include_extensions = tuple(args.include.split(','))

    commit_to_file(args.path, args.commit, include_extensions)
