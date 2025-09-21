# Contributing

We'd love your help making Notionary even better! 🚀

## Quick Setup

### Prerequisites

- Python 3.9+
- uv (install from [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/))

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/yourusername/notionary.git
   cd notionary
   ```

2. **Install dependencies with uv**

   ```bash
   uv sync --all-extras
   ```

3. **Install pre-commit hooks**

   ```bash
   uv run pre-commit install
   ```

4. **Run tests to verify setup**
   ```bash
   uv run pytest
   ```

### Making Changes

1. **Create a new branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and test**

   ```bash
   # Run tests
   uv run pytest

   # Run linting and formatting (or let pre-commit handle it)
   uv run ruff check .
   uv run ruff format .

   # Type checking
   uv run mypy notionary
   ```

3. **Commit and push**

   ```bash
   git add .
   git commit -m "Add your feature description"
   # Pre-commit hooks will automatically run and fix formatting
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request**

## Development Tools

- **Ruff** handles linting and code formatting
- **MyPy** for type checking
- **Pre-commit** automatically runs checks before each commit
- **Pytest** for testing

## What We're Looking For

- 🐛 **Bug fixes** - Found something broken? Fix it!
- ✨ **New features** - Ideas for improvements or new functionality
- 📚 **Documentation** - Help make our docs clearer and more complete
- 🧪 **Tests** - More test coverage is always welcome
- 🎨 **Examples** - Real-world usage examples and tutorials

## Guidelines

- Keep changes focused and atomic
- Add tests for new functionality
- Update documentation as needed
- Follow existing code style (enforced by Ruff and pre-commit)
- Be descriptive in commit messages
- Let pre-commit handle formatting - don't worry about manual formatting

## Code Quality

The project uses:

- **Ruff** for fast linting and formatting
- **MyPy** for type checking
- **Pre-commit hooks** that automatically run before commits
- **Pytest** for comprehensive testing

When you commit, pre-commit will automatically:

- Format your code with Ruff
- Fix common linting issues
- Run type checking
- Perform security checks

**All contributions are very welcome!** No contribution is too small - from fixing typos to adding major features, we appreciate it all.

Thanks for helping make Notionary awesome! 🙏
