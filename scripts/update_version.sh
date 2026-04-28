#!/usr/bin/env bash
set -e

script_dir=$(cd "$(dirname "$0")" && pwd)

current_version=$(\
    grep "version = \"\(.*\)\"" "$script_dir"/../pyproject.toml \
    | sed "s/version = \"\(.*\)\"/\1/g"
)
escaped_current_version=${current_version//\./\\\.}

if [ $# -ne 1 ]; then
    echo "Usage: $0 <new-version>"
    exit 1
fi

new_version=$1

cd "$script_dir"/.. || exit

if git tag --list | grep "v$new_version" &> /dev/null; then
    echo "Version '$new_version' is already a local tag"
    exit 1
fi

if git ls-remote --tags --quiet | cut -f 2 | cut -d"/" -f 3 | grep "v$new_version" &> /dev/null; then
    echo "Version '$new_version' is already a remote tag"
    exit 1
fi

git checkout develop
git pull

make tests
make check

git checkout -b "release-v$new_version"

escaped_new_version=${new_version//\./\\\.}

files_to_check=(\
    "README.md"
    "pyproject.toml"
)

for file in "${files_to_check[@]}"; do
    sed -i "s/$escaped_current_version/$escaped_new_version/g" "$file"
    git add "$file"
done

make check
git add uv.lock

git commit -m "chore: v$new_version"
git push --set-upstream origin "release-v$new_version"

git checkout main
git merge "release-v$new_version"
git push

git tag "v$new_version"
git push --tags

git checkout develop
git merge main
git push
