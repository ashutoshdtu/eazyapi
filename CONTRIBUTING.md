# Contributing to EazyAPI

👏🎉 First off all, Thanks for your interest in contributing to our project! 🎉👏

The following is a set of guidelines for contributing to EazyAPI. These are
mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

We take our open source community seriously and hold ourselves and other contributors to high standards of communication. By participating and contributing to this project, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Requirements

We use `poetry` to manage and install dependencies. [Poetry](https://python-poetry.org/) provides a custom installer that will install `poetry` isolated from the rest of your system.

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
```

We'll also need `nox` for automated testing in multiple Python environments so [install that too](https://nox.thea.codes/en/stable/).

```
pip install --user --upgrade nox
```

We use [`commitizen`](https://commitizen-tools.github.io/) for better commit messages, CHANGELOG generation and version bumps. To install:

```
pip install --user -U Commitizen
```

To install the local development requirements inside a virtual environment run:

```
$ poetry install
$ poetry run inv install-hooks
```

> For more information about `poetry` check the [docs](https://python-poetry.org/docs/).

We use [invoke](http://www.pyinvoke.org/) to wrap up some useful tasks like formatting, linting, testing and more.

Execute `poetry run inv[oke] --list` to see the list of available commands.

## Contributing

### Issues

We use GitHub issues to track public bugs/enhancements. Report a new one by [opening a new issue](https://github.com/ashutoshdtu/eazyapi/issues).

In this repository, we provide a couple of templates for you to fill in for:

* Bugs
* Feature Requests/Enhancements

Please read each section in the templates and provide as much information as you can. Please do not put any sensitive information,
such as personally identifiable information, connection strings or cloud credentials. The more information you can provide, the better we can help you.

### Pull Requests

Please follow these steps to have your contribution considered by the maintainers:

1. Fork the repo and create your branch locally with a succinct but descriptive name.
2. Add tests for the new changes
3. Edit documentation if you have changed something significant
4. Make sure to follow the [styleguides](#styleguides)
5. Use `cz commit -s` instead of `git commit` to commit your changes
6. Open a PR in our repository and follow the PR template so that we can efficiently review the changes
7. After you submit your pull request, verify that all status checks are passing

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design
work, tests, or other changes before your pull request can be ultimately accepted.

### Commit Messages

We use [`commitizen`](https://commitizen-tools.github.io/) and follow the [Conventional Commits](https://www.conventionalcommits.org/) and [Semantic Versioning](https://semver.org/) guidelines for our commits. Here are some recommendations for writing commit messages:

- **Keep the message short**: Makes the list of commits more readable (~50 chars).
- **Talk imperative**: Follow this rule: `If applied, this commit will <commit message>`
- **Think about the CHANGELOG**: Your commits will probably end up in the changelog so try writing for it, but also keep in mind that you can skip sending commits to the CHANGELOG by using different keywords (like build).
- **Use a commit per new feature**: if you introduce multiple things related to the same commit, squash them. This is useful for auto-generating CHANGELOG.


## Styleguides

### Python Code Style

All Python code is linted with [Flake8](https://github.com/PyCQA/flake8) and formated with
[Isort](https://github.com/PyCQA/isort) and [Black](https://github.com/psf/black). You can
execute `inv[oke] lint` and `inv[oke] format`.

## Additional Notes

If you have any question feel free to contact us at ashutoshdtu@gmail.com.
