# Bulleted List Blocks

Bulleted lists organize information in unordered, scannable format. Perfect for features, benefits, requirements, and any content where order doesn't matter.

## Basic Syntax

```markdown
- First item
- Second item
- Third item
```

Alternative bullet markers:

```markdown
- First item
- Second item
- Third item

* First item
* Second item
* Third item
```

## Simple Lists

### Feature Lists

```markdown
## Core Features

- Real-time collaboration
- Advanced analytics
- Custom integrations
- 24/7 support
- Mobile applications
```

### Requirements

```markdown
## System Requirements

- Python 3.8 or higher
- 4GB RAM minimum
- 10GB available disk space
- Internet connection
- Modern web browser
```

### Benefits

```markdown
## Why Choose Our Platform

- Reduce development time by 50%
- Improve team collaboration
- Scale automatically with demand
- Enterprise-grade security
- Comprehensive documentation
```

## Rich Text Lists

### Formatted Content

```markdown
## Development Tools

- **Code Editor**: VS Code with Python extension
- **Version Control**: Git with _GitHub_ or _GitLab_
- **Package Manager**: `pip` for Python dependencies
- **Testing Framework**: `pytest` for unit testing
- **Documentation**: Sphinx for API docs
```

### Lists with Links

```markdown
## Useful Resources

- [Official Documentation](https://docs.example.com)
- [Community Forum](https://forum.example.com)
- [GitHub Repository](https://github.com/example/repo)
- [Video Tutorials](https://tutorials.example.com)
- [API Reference](https://api.example.com)
```

### Technical Specifications

```markdown
## API Endpoints

- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `GET /api/users/{id}` - Get specific user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
```

## Nested Lists

### Multi-level Organization

```markdown
## Project Structure

- Frontend
  - React components
  - CSS stylesheets
  - JavaScript modules
- Backend
  - API routes
  - Database models
  - Authentication logic
- Documentation
  - User guides
  - API reference
  - Developer notes
```

### Categorized Information

```markdown
## Programming Languages

- **Frontend**
  - JavaScript
  - TypeScript
  - HTML/CSS
- **Backend**
  - Python
  - Node.js
  - Java
- **Mobile**
  - Swift (iOS)
  - Kotlin (Android)
  - React Native
```

### Detailed Breakdowns

```markdown
## Implementation Plan

- Phase 1: Foundation
  - Set up development environment
  - Create basic project structure
  - Implement authentication system
  - Write initial documentation
- Phase 2: Core Features
  - Build main user interface
  - Develop API endpoints
  - Add data validation
  - Create test suite
- Phase 3: Advanced Features
  - Add real-time notifications
  - Implement search functionality
  - Create admin dashboard
  - Optimize performance
```

## Mixed Content Lists

### Lists with Code

````markdown
## Configuration Steps

- Install required packages:
  ```bash
  pip install flask sqlalchemy
  ```
````

- Set environment variables:
  ```bash
  export FLASK_ENV=development
  export DATABASE_URL=postgresql://localhost/mydb
  ```
- Run the application:
  ```bash
  flask run
  ```

````

### Lists with Examples

```markdown
## Data Types
- **String**: Text data
  - Example: `"Hello, World!"`
  - Use for names, descriptions, messages
- **Integer**: Whole numbers
  - Example: `42`, `-17`, `0`
  - Use for counts, IDs, quantities
- **Boolean**: True/false values
  - Example: `True`, `False`
  - Use for flags, settings, conditions
````

## Programmatic Usage

### Creating Bulleted Lists

```python
from notionary.blocks.bulleted_list import BulletedListMarkdownNode

# Simple list
features = BulletedListMarkdownNode(
    texts=[
        "Fast performance",
        "Easy integration",
        "Comprehensive documentation",
        "24/7 support"
    ]
)

markdown = features.to_markdown()
```

### Dynamic List Generation

```python
def create_feature_list(features):
    feature_items = []
    for feature in features:
        if feature.get("highlight"):
            item = f"**{feature['name']}**: {feature['description']}"
        else:
            item = f"{feature['name']}: {feature['description']}"
        feature_items.append(item)

    return BulletedListMarkdownNode(texts=feature_items)

# Usage
app_features = [
    {"name": "Real-time Sync", "description": "Data updates instantly", "highlight": True},
    {"name": "Offline Mode", "description": "Works without internet"},
    {"name": "Cloud Backup", "description": "Automatic data protection", "highlight": True}
]

feature_list = create_feature_list(app_features)
await page.append_markdown(feature_list.to_markdown())
```

### Using with Pages

```python
import asyncio
from notionary import NotionPage

async def create_getting_started_guide():
    page = await NotionPage.from_page_name("Getting Started")

    guide_content = '''
# Getting Started Guide

## Prerequisites
Before you begin, make sure you have:
- Python 3.8 or higher installed
- A text editor or IDE
- Basic knowledge of Python
- Internet connection for downloads

## Installation Steps
- Download the latest release from our website
- Extract the files to your desired location
- Open a terminal in the project directory
- Run the installation command
- Verify the installation was successful

## Initial Configuration
- Create a new configuration file
- Set your API credentials
- Choose your preferred settings
- Test the connection
- Save your configuration

## Next Steps
- Read the [User Guide](user-guide.md)
- Try the [Quick Tutorial](tutorial.md)
- Join our [Community Forum](forum-link)
- Follow us on [GitHub](github-link)
    '''

    await page.replace_content(guide_content)

asyncio.run(create_getting_started_guide())
```

## Documentation Patterns

### API Documentation

```markdown
## Authentication Methods

Our API supports multiple authentication methods:

- **API Key Authentication**

  - Include `X-API-Key` header with requests
  - Suitable for server-to-server communication
  - No expiration (rotate regularly for security)

- **OAuth 2.0**

  - Standard OAuth 2.0 flow implementation
  - Recommended for user-facing applications
  - Secure token-based authentication

- **JWT Tokens**
  - Stateless authentication mechanism
  - Include bearer token in Authorization header
  - Configurable expiration times
```

### Feature Comparison

```markdown
## Plan Comparison

### Free Plan

- Up to 3 team members
- 5GB storage space
- Basic integrations
- Email support only
- Community access

### Pro Plan

- Up to 25 team members
- 100GB storage space
- Advanced integrations
- Priority email support
- Phone support available
- Advanced analytics

### Enterprise Plan

- Unlimited team members
- 1TB storage space
- Custom integrations
- Dedicated account manager
- 24/7 phone support
- Custom reporting
- Single sign-on (SSO)
```

### Troubleshooting Guides

```markdown
## Common Issues

### Installation Problems

- **Error: Python not found**

  - Ensure Python 3.8+ is installed
  - Check your PATH environment variable
  - Restart your terminal after installation

- **Error: Permission denied**

  - Run terminal as administrator (Windows)
  - Use `sudo` prefix (macOS/Linux)
  - Check file permissions in install directory

- **Error: Package conflicts**
  - Create a virtual environment
  - Update pip to latest version
  - Clear pip cache: `pip cache purge`

### Runtime Errors

- **Connection timeout**

  - Check internet connectivity
  - Verify API endpoint URLs
  - Review firewall settings
  - Try increasing timeout values

- **Authentication failed**
  - Verify API credentials
  - Check token expiration
  - Ensure proper header format
  - Test with different credentials
```

## Visual Organization

### Scannable Content

```markdown
# ✅ Good - Clear, scannable lists

## Key Benefits

- Increased productivity
- Reduced development time
- Better code quality
- Improved team collaboration

# ✅ Good - Consistent formatting

## Supported Platforms

- **Windows**: 10, 11
- **macOS**: Big Sur, Monterey, Ventura
- **Linux**: Ubuntu 20.04+, CentOS 8+

# ❌ Avoid - Inconsistent or cluttered

## Features

- some feature
- Another Feature With Different Capitalization
- feature with way too much detail that should probably be broken down
- Short one
```

### Logical Grouping

```markdown
## Development Workflow

### Planning Phase

- Define project requirements
- Create user stories and acceptance criteria
- Design system architecture
- Set up project timeline

### Development Phase

- Set up development environment
- Implement core functionality
- Write comprehensive tests
- Document API endpoints

### Testing Phase

- Run unit and integration tests
- Perform security audits
- Conduct user acceptance testing
- Load test for performance

### Deployment Phase

- Prepare production environment
- Deploy to staging first
- Monitor system performance
- Roll out to production
```

## Best Practices

### Content Structure

```markdown
# ✅ Good - Parallel structure

## Setup Requirements

- Install Python 3.8+
- Configure virtual environment
- Install dependencies
- Set environment variables

# ✅ Good - Action-oriented items

## Getting Started

- Download the installer
- Run the setup wizard
- Configure your preferences
- Launch the application

# ❌ Avoid - Mixed structures

## Requirements

- Python 3.8+
- You need to configure environment
- Dependencies should be installed
- Setting up variables
```

### Length and Clarity

```markdown
# ✅ Good - Concise, clear items

## Core Features

- Real-time collaboration
- Advanced analytics
- Custom integrations
- Mobile applications

# ❌ Avoid - Overly long items

## Features

- Real-time collaboration that allows multiple users to work together simultaneously on the same project with live updates and conflict resolution
- Advanced analytics with comprehensive reporting, data visualization, and business intelligence capabilities
```

## Integration with Other Blocks

### Lists with Callouts

```markdown
## Installation Guide

[callout](💡 **Tip:** Use a virtual environment to avoid dependency conflicts "💡")

- Create virtual environment: `python -m venv venv`
- Activate environment: `source venv/bin/activate`
- Install packages: `pip install -r requirements.txt`
- Verify installation: `python --version`

[callout](⚠️ **Important:** Always activate your virtual environment before working "⚠️")
```

### Lists in Toggles

```markdown
+++ Advanced Configuration Options
- Custom authentication providers
- Advanced caching strategies
- Load balancing configuration
- SSL certificate management
- Database optimization settings
- Monitoring and alerting setup
+++
```

### Lists in Columns

```markdown
::: columns
::: column

## Frontend Technologies

- React.js
- TypeScript
- Tailwind CSS
- Next.js
- Vercel deployment
  :::
  ::: column

## Backend Technologies

- Python Flask
- PostgreSQL
- Redis caching
- Docker containers
- AWS hosting
  :::
  :::
```

### Lists in Tables

```markdown
| Category | Technologies                         |
| -------- | ------------------------------------ |
| Frontend | • React<br>• Vue.js<br>• Angular     |
| Backend  | • Node.js<br>• Python<br>• Java      |
| Database | • PostgreSQL<br>• MongoDB<br>• Redis |
```

## Related Blocks

- **[Numbered List](numbered-list.md)** - For ordered, sequential content
- **[To Do](todo.md)** - For task lists with checkboxes
- **[Toggle](toggle.md)** - For collapsible list sections
- **[Callout](callout.md)** - For highlighting important list items
