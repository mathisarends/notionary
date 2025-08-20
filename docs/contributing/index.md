# Contributing

We'd love your help making Notionary even better! 🚀

## Quick Setup

### Prerequisites

- Python 3.8+
- Poetry (install from [python-poetry.org](https://python-poetry.org/docs/#installation))

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/yourusername/notionary.git
   cd notionary
   ```

2. **Install dependencies with Poetry**

   ```bash
   poetry install
   ```

3. **Activate the virtual environment**

   ```bash
   poetry shell
   ```

4. **Run tests to verify setup**
   ```bash
   poetry run pytest
   ```

### Making Changes

1. **Create a new branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and test**

   ```bash
   # Run tests
   poetry run pytest

   # Run linting
   poetry run black .
   poetry run isort .
   ```

3. **Commit and push**

   ```bash
   git add .
   git commit -m "Add your feature description"
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request**

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
- Follow existing code style (Black + isort)
- Be descriptive in commit messages

**All contributions are very welcome!** No contribution is too small - from fixing typos to adding major features, we appreciate it all.

Thanks for helping make Notionary awesome! 🙏
