import argparse
import git
import os


def latest_commit_to_file(repo_path):
    repo = git.Repo(repo_path)

    # Get the latest commit
    commit = repo.head.commit

    # Get the commit message
    commit_message = commit.message

    # Get the diff
    diff = commit.diff('HEAD~1', create_patch=True)

    diff_text = "".join(d.__str__() for d in diff.iter_change_type('M'))

    # Define output file name
    output_file = os.path.join(repo_path, f"{commit.hexsha}.txt")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Commit Message:\n" + commit_message + "\n")
        f.write("Diff:\n" + diff_text)

    print(f"Commit information written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Write latest commit info to a file.")
    parser.add_argument("path", help="Path to the git repository.")

    args = parser.parse_args()

    latest_commit_to_file(args.path)
