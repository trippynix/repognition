## Contributing to Repo-gnition

First off, thank you for considering contributing to Repo-gnition! We're excited to have you join our community. Your help is essential for making this tool better for everyone.

This document provides guidelines for contributing to the project. Whether you're reporting a bug, proposing a new feature, or writing code, these guidelines are here to help you get started.

## Code of Conduct

To ensure a welcoming and inclusive community, we have a [Code of Conduct](CODE_OF_CONDUCT.md) that all contributors are expected to follow. Please take a moment to read it before participating.

## How Can I Contribute?

There are many ways you can contribute to Repo-gnition, and not all of them involve writing code.

- 🐛 Reporting Bugs: If you find a bug, please open an issue and provide as much detail as possible.

- 💡 Suggesting Enhancements: Have an idea for a new feature or an improvement to an existing one? We'd love to hear it! Open an issue to start a discussion.

- 📖 Improving Documentation: If you find parts of the documentation that are unclear or could be improved, you can edit them and submit a pull request.

- 💻 Writing Code: If you're ready to write some code, you can start by looking at our open issues, especially those tagged with `good first issue` or `help wanted`.

## Getting Started: Your First Contribution

Ready to dive in? Here's how you can set up your development environment and submit your first pull request.

### 1. Fork and Clone the Repository

First, fork the repository to your own GitHub account. Then, clone your fork to your local machine:

```bash
git clone https://github.com/your-username/repognition.git
cd repognition
```

### 2. Sync Your Fork

Before creating a new branch, make sure your fork is up-to-date with the main project. First, configure the original repository as the "upstream" remote:

```bash
git remote add upstream https://github.com/your-username/repognition.git
```

Now, pull the latest changes from the upstream main branch to ensure you're working with the most recent version:

```bash
git pull upstream main
```

### 3. Set Up the Development Environment

We recommend using a Python virtual environment to keep dependencies isolated.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the project in editable mode with all dependencies
pip install -e .
```

### 4. Create a New Branch

Create a new branch for your changes. Please use a descriptive name that reflects the feature or fix you're working on.

```bash
# For a new feature
git checkout -b feature/your-feature-name

# For a bug fix
git checkout -b fix/your-bug-fix
```

### 5. Write Your Code

Now you can start making your changes! As you work, please keep the following in mind:

- **Coding Style**: We use the `black` code formatter to maintain a consistent style. Please run `black .` before committing your changes.

- **Commit Messages**: Please write clear and concise commit messages. We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

  - Example: `feat: Add support for parsing TypeScript files`

  - Example: `fix: Correctly handle line numbers in the chunker`

- **Keep it Focused**: Each pull request should address a single issue or feature. Avoid bundling multiple unrelated changes into one PR.

### 6. Submit a Pull Request

Once you're happy with your changes, push your branch to your fork and open a pull request against the `main` branch of the original repository.

In your pull request description, please:

- **Link to the relevant issue** (e.g., "Closes #123").

- **Describe your changes** clearly and concisely.

- **Explain the "why"** behind your changes.

## Reporting Bugs

To report a bug, please [open an issue](https://github.com/trippynix/AI-DevAssistant/issues/new) and include the following information:

- **A clear and descriptive title.**

- **Steps to reproduce the bug.**

- **What you expected to happen.**

- **What actually happened.**

- **Your system information** (OS, Python version, etc.).

## Suggesting Enhancements

To suggest an enhancement, please [open an issue](https://github.com/trippynix/AI-DevAssistant/issues/new) and provide:

- **A clear and descriptive title.**

- **A detailed description of the proposed enhancement.**

- **An explanation of why this would be a valuable addition to the project.**

Thank you again for your interest in contributing to Repo-gnition! We look forward to your contributions.
