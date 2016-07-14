git push --tags origin master
python setup.py register -r pypi
python setup.py sdist upload -r pypi
