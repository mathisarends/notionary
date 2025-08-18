# Image Blocks

Image blocks embed visual content from URLs or uploaded files. Essential for documentation, tutorials, and visual storytelling.

## Basic Syntax

```markdown
[image](https://example.com/image.jpg)
[image](https://example.com/image.png "Caption text")
```

## Image Sources

### External URLs

```markdown
# Direct image URLs

[image](https://images.unsplash.com/photo-example.jpg)
[image](https://cdn.example.com/screenshots/dashboard.png)

# With descriptive captions

[image](https://example.com/diagram.svg "System Architecture Diagram")
[image](https://assets.company.com/logo.png "Company Logo")
```

### Common Image Formats

```markdown
# Raster formats

[image](https://example.com/photo.jpg "JPEG photograph")
[image](https://example.com/graphic.png "PNG with transparency")
[image](https://example.com/animation.gif "Animated GIF demo")

# Vector formats

[image](https://example.com/diagram.svg "Scalable vector diagram")
[image](https://example.com/icon.svg "Vector icon")

# Web formats

[image](https://example.com/optimized.webp "WebP optimized image")
```

## Documentation Images

### Screenshots and UI

```markdown
## Dashboard Overview

Here's what you'll see when you first log in:

[image](https://docs.example.com/screenshots/dashboard-home.png "Dashboard home screen")

### Key Features:

1. **Navigation** - Left sidebar with main sections
2. **Quick Actions** - Top toolbar for common tasks
3. **Activity Feed** - Center panel with recent updates
4. **Stats Widget** - Right panel with key metrics

## Settings Configuration

Navigate to the settings page:

[image](https://docs.example.com/screenshots/settings-general.png "General settings panel")

Configure these important options:

- **API Access** - Enable/disable API endpoints
- **Notifications** - Email and push preferences
- **Security** - Two-factor authentication setup
```

### Step-by-step Guides

```markdown
## Installation Guide

### Step 1: Download

Click the download button in the top right:

[image](https://help.example.com/install/step1-download.png "Download button location")

### Step 2: Run Installer

Double-click the downloaded file:

[image](https://help.example.com/install/step2-installer.png "Installation wizard welcome screen")

### Step 3: Choose Options

Select your installation preferences:

[image](https://help.example.com/install/step3-options.png "Installation options dialog")

### Step 4: Complete Setup

Wait for installation to finish:

[image](https://help.example.com/install/step4-complete.png "Installation complete confirmation")
```

### Before/After Comparisons

```markdown
## UI Improvements

### Before: Old Interface

[image](https://updates.example.com/v1/old-interface.png "Previous version interface")

### After: New Interface

[image](https://updates.example.com/v2/new-interface.png "Updated modern interface")

### Key Improvements:

- **Cleaner Layout** - Reduced visual clutter
- **Better Navigation** - Intuitive menu structure
- **Responsive Design** - Works on all devices
- **Accessibility** - Enhanced screen reader support
```

## Technical Diagrams

### Architecture Diagrams

```markdown
## System Architecture

Our platform follows a microservices architecture:

[image](https://docs.example.com/diagrams/architecture-overview.svg "High-level system architecture")

### Component Breakdown:

#### Frontend Layer

- **React SPA** - User interface
- **Redux Store** - State management
- **API Client** - Backend communication

#### Backend Services

- **API Gateway** - Request routing
- **Auth Service** - User authentication
- **Data Service** - Database operations
- **Queue Service** - Async processing

#### Infrastructure

- **Load Balancer** - Traffic distribution
- **Database Cluster** - Data persistence
- **Redis Cache** - Performance optimization
```

### Flow Diagrams

```markdown
## Authentication Flow

[image](https://docs.example.com/diagrams/auth-flow.svg "OAuth 2.0 authentication flow")

### Process Steps:

1. **User Login** - User enters credentials
2. **Validate** - System checks username/password
3. **Generate Token** - Create JWT with user info
4. **Return Token** - Send token to client
5. **Store Token** - Client saves for future requests

## Data Processing Pipeline

[image](https://docs.example.com/diagrams/data-pipeline.svg "Data processing workflow")

Raw data flows through multiple stages:

- **Ingestion** → **Validation** → **Transform** → **Store** → **Analyze**
```

## Visual Examples

### Code Output

````markdown
## Chart Generation Example

Using our charting library:

```python
import matplotlib.pyplot as plt

# Generate sample data
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# Create chart
plt.plot(x, y)
plt.title("Sample Data Visualization")
plt.show()
```
````

Generated output:

[image](https://examples.example.com/charts/sample-chart.png "Sample matplotlib chart output")

````

### API Response Examples

```markdown
## API Response Format

When you call the `/api/users` endpoint:

```json
{
  "users": [
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob", "role": "user"}
  ],
  "total": 2,
  "page": 1
}
````

Visual representation:

[image](https://docs.example.com/api/users-response.png "API response visualization")

````

## Programmatic Usage

### Creating Image Blocks

```python
from notionary.blocks.image import ImageMarkdownNode

# Simple image
image = ImageMarkdownNode(
    url="https://example.com/image.jpg",
    caption="Descriptive caption"
)

markdown = image.to_markdown()
````

### Using with Pages

```python
import asyncio
from notionary import NotionPage

async def add_documentation_images():
    page = await NotionPage.from_page_name("User Guide")

    guide_content = '''
# User Interface Guide

## Main Dashboard

When you first log in, you'll see the main dashboard:

[image](https://docs.example.com/ui/dashboard.png "Main dashboard overview")

## Navigation Menu

The left sidebar contains all major sections:

[image](https://docs.example.com/ui/navigation.png "Navigation sidebar menu")

## Settings Panel

Access your account settings from the top-right menu:

[image](https://docs.example.com/ui/settings.png "User settings panel")
    '''

    await page.replace_content(guide_content)

asyncio.run(add_documentation_images())
```

### Dynamic Image Generation

```python
def create_comparison_doc(old_version, new_version):
    return f'''
# Version Comparison: {old_version} vs {new_version}

## Previous Version ({old_version})
[image](https://releases.example.com/v{old_version}/screenshot.png "Version {old_version} interface")

## Current Version ({new_version})
[image](https://releases.example.com/v{new_version}/screenshot.png "Version {new_version} interface")

## Key Changes
- Improved user experience
- Enhanced performance
- New feature additions
- Bug fixes and stability improvements
'''

# Usage
comparison = create_comparison_doc("1.2", "1.3")
await page.replace_content(comparison)
```

## Image Organization

### Gallery Layout

```markdown
# Product Gallery

## Screenshots

### Desktop Application

[image](https://gallery.example.com/desktop-main.png "Desktop app main window")
[image](https://gallery.example.com/desktop-settings.png "Desktop app settings")
[image](https://gallery.example.com/desktop-projects.png "Desktop app project view")

### Mobile Application

[image](https://gallery.example.com/mobile-home.png "Mobile app home screen")
[image](https://gallery.example.com/mobile-menu.png "Mobile app navigation menu")
[image](https://gallery.example.com/mobile-profile.png "Mobile app user profile")

### Web Interface

[image](https://gallery.example.com/web-dashboard.png "Web dashboard")
[image](https://gallery.example.com/web-analytics.png "Web analytics page")
[image](https://gallery.example.com/web-reports.png "Web reports section")
```

### Feature Showcase

```markdown
# Feature Highlights

## Real-time Collaboration

See multiple users working together:

[image](https://features.example.com/collaboration.gif "Real-time collaboration demo")

## Advanced Analytics

Comprehensive data visualization:

[image](https://features.example.com/analytics-dashboard.png "Analytics dashboard with charts")

## Mobile Responsiveness

Seamless experience across devices:

[image](https://features.example.com/responsive-design.png "Responsive design showcase")
```

## Best Practices

### Image Quality and Accessibility

```markdown
# ✅ Good - Clear, descriptive captions

[image](https://docs.example.com/setup/step1.png "Step 1: Click the 'New Project' button in the top toolbar")

# ✅ Good - Appropriate image resolution

[image](https://docs.example.com/hires/dashboard.png "High-resolution dashboard screenshot (1920x1080)")

# ❌ Avoid - Missing or vague captions

[image](https://example.com/image.png "Image")

# ❌ Avoid - Poor quality images

[image](https://example.com/blurry.jpg "Blurry screenshot")
```

### Context and Integration

```markdown
## Proper Context Example

Follow these steps to configure your workspace:

1. **Open Settings** - Click the gear icon in the top right
2. **Navigate to Workspace** - Select the "Workspace" tab

[image](https://help.example.com/workspace-settings.png "Workspace settings panel with highlighted options")

3. **Configure Options** - Adjust settings as needed:
   - **Team Name** - Your organization's display name
   - **Default Role** - Permissions for new members
   - **Privacy** - Public or private workspace

The settings panel shows all available configuration options.
```

### Performance Optimization

```markdown
# Image Loading Considerations

## Recommended Practices:

- **Optimize file sizes** - Compress images without quality loss
- **Use appropriate formats** - JPEG for photos, PNG for graphics, SVG for icons
- **Provide alt text** - Descriptive captions for accessibility
- **Consider mobile** - Ensure images work on small screens

## CDN Usage:

Store images on a reliable CDN for fast loading:

- `https://cdn.example.com/` - Global CDN with edge caching
- `https://images.example.com/` - Optimized image delivery
```

## Integration with Other Blocks

### Images with Callouts

```markdown
## Important Setup Step

[callout](⚠️ **Critical:** Complete this configuration exactly as shown "⚠️")

[image](https://setup.example.com/critical-step.png "Required configuration settings")

[callout](✅ **Success:** You should see a green checkmark when done correctly "✅")
```

### Images in Toggles

```markdown
+++ Advanced Configuration Screenshots
For users who need detailed visual guidance:

[image](https://advanced.example.com/config1.png "Advanced settings panel")
[image](https://advanced.example.com/config2.png "Expert configuration options")
[image](https://advanced.example.com/config3.png "Custom integration settings")
+++
```

### Images in Columns

```markdown
::: columns
::: column

## Before Optimization

[image](https://perf.example.com/before.png "Slow loading interface")

**Issues:**

- Long load times
- Poor responsiveness
- High resource usage
  :::
  ::: column

## After Optimization

[image](https://perf.example.com/after.png "Optimized fast interface")

**Improvements:**

- 3x faster loading
- Smooth interactions
- Reduced resource usage
  :::
  :::
```

## Related Blocks

- **[Video](video.md)** - For moving visual content
- **[File](file.md)** - For downloadable image files
- **[Callout](callout.md)** - For highlighting image context
- **[Toggle](toggle.md)** - For collapsible image galleries
