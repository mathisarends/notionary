# Numbered List Blocks

Numbered lists present information in ordered, sequential steps. Ideal for instructions, procedures, or priorities.

## Basic Syntax

```markdown
1. First step
2. Second step
3. Third step
```

## Quick Examples

```markdown
## Installation Process

1. Download the installer
2. Run the setup wizard
3. Restart your computer
```

```markdown
## Database Setup

1. Install PostgreSQL
2. Create a new database
3. Configure connection parameters
```

```markdown
## Development Priorities

1. Fix security vulnerabilities
2. Add authentication system
3. Improve performance
```

## Nested Lists

```markdown
## Project Setup Guide

1. **Environment Preparation**
   1. Install Python 3.8+
   2. Set up virtual environment
2. **Project Initialization**
   1. Clone repository
   2. Configure database
```

## Mixed Content

```markdown
## API Client Setup

1. Install the SDK: `pip install notionary-client`
2. Import modules: `from notionary import NotionClient`
3. Initialize the client
4. Test the connection
```

## Programmatic Usage

### Using MarkdownBuilder

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("Setup Instructions")
    .numbered_list([
        "Download the latest release",
        "Extract the files",
        "Open a terminal in the project directory",
        "Run the installation command",
        "Verify the installation"
    ])
    .h2("Configuration Steps")
    .numbered_list([
        "**Create Config**: Set up configuration file",
        "**Add Credentials**: Include API keys",
        "**Test Connection**: Verify setup",
        "**Save Settings**: Store configuration"
    ])
)

print(builder.build())
```
