#!/bin/bash

start_time=$(date +%s)


poetry config virtualenvs.create true
poetry config virtualenvs.in-project true

git submodule update --init --recursive
if [ $? -ne 0 ]; then
    echo "``git submodule update --init --recursive`` failed. Exiting."
    exit 1
fi

poetry lock
if [ $? -ne 0 ]; then
    echo "``poetry lock`` failed. Exiting."
    exit 1
fi

poetry install
if [ $? -ne 0 ]; then
    echo "``poetry install`` failed. Exiting."
    exit 1
fi

poetry run build-grammar
if [ $? -ne 0 ]; then
    echo "``poetry run build-grammar`` failed. Exiting."
    exit 1
fi

poetry run pytest -s -v --disable-warnings --html=report.html
if [ $? -ne 0 ]; then
    echo "``poetry run pytest`` failed. Exiting."
    exit 1
fi

echo "================Formatting code"
poetry run black ./ --exclude '(\/(\.venv|vendor|build)\/)' --line-length 100 -q
if [ $? -ne 0 ]; then
    echo "``black`` failed. Exiting."
    exit 1
fi

# run static code analysis, excluding the .venv directory
echo "================Running static code analysis"
poetry run pylint  --rcfile=tools/.pylintrc ./ --disable=all --enable=F
if [ $? -ne 0 ]; then
    echo "``Linter`` failed. Exiting."
    exit 1
fi

end_time=$(date +%s)
elapsed=$((end_time - start_time))
minutes=$((elapsed / 60))
seconds=$((elapsed % 60))

# Format output
if [[ $minutes -gt 0 ]]; then
    echo "Time: ${minutes} min ${seconds} sec"
else
    echo "Time: ${seconds} sec"
fi

echo "===BUILD SUCCESS==="