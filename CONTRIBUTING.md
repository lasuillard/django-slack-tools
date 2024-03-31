# 💝 Contributing

Thank you for your interest in contributing to our project. Before contributing, please check [existing issues](https://github.com/lasuillard/django-slack-tools/issues). If there is a bug or feature that is not listed, create a new issue and make changes on it.

## ⚙️ Developing

### 🍴 [Fork the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

### 🐋 Set up development environment

This project repository has configured development container. Get a quick start with [GitHub Codespaces](https://github.com/features/codespaces) or [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/tutorial).

### 🖊️ Format and lint codes

We use [Ruff](https://github.com/astral-sh/ruff) to format codes and check types using [mypy](https://mypy-lang.org/). Format codes with:

```bash
$ make format
$ make lint
```

### ✅ Test your changes

Once changes made, it should be tested. We use [pytest](https://docs.pytest.org/en/8.0.x/) for testing.

Run tests with:

```bash
$ make test
```

### ✨ [Create PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)

We will review your PR and reply as soon as possible.

## 🗒️ Docs

Docs are generated using [MkDocs](https://www.mkdocs.org/). To see docs locally with live reloading:

```bash
$ make serve-docs
```

Go to http://localhost:8000 and you will see the docs preview.

## 🔗 Resources

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
