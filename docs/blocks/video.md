# Video Blocks

Video blocks embed video content from popular platforms or direct file URLs. Perfect for tutorials, demos, and multimedia documentation.

## Basic Syntax

```markdown
[video](https://youtube.com/watch?v=VIDEO_ID)
[video](https://vimeo.com/VIDEO_ID)
[video](https://example.com/video.mp4)
```

## Supported Platforms

### YouTube Videos

```markdown
# Full YouTube URLs

[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
[video](https://youtube.com/watch?v=dQw4w9WgXcQ)

# Short YouTube URLs

[video](https://youtu.be/dQw4w9WgXcQ)

# YouTube with timestamp

[video](https://youtube.com/watch?v=dQw4w9WgXcQ&t=120)
```

### Vimeo Videos

```markdown
# Standard Vimeo URLs

[video](https://vimeo.com/123456789)
[video](https://player.vimeo.com/video/123456789)

# Vimeo with privacy settings

[video](https://vimeo.com/123456789/private_hash)
```

### Direct Video Files

```markdown
# Direct MP4 files

[video](https://example.com/demo.mp4)
[video](https://cdn.example.com/tutorial.mp4)

# Other video formats

[video](https://example.com/presentation.webm)
[video](https://example.com/recording.mov)
```

## Videos with Captions

### Descriptive Captions

```markdown
[video](https://youtube.com/watch?v=demo123 "Product Demo - New Features")
[video](https://vimeo.com/987654321 "Team Introduction Video")
[video](https://example.com/tutorial.mp4 "Step-by-step Installation Guide")
```

### Contextual Information

```markdown
[video](https://youtube.com/watch?v=api_tutorial "Duration: 15 min | Beginner Level")
[video](https://vimeo.com/conference_talk "Conference 2024 - Keynote Presentation")
```

## Common Use Cases

### Documentation and Tutorials

```markdown
## Getting Started

Watch our quick introduction video:

[video](https://youtube.com/watch?v=intro123 "Notionary Introduction - 5 minutes")

### Installation Guide

Follow along with the step-by-step installation:

[video](https://youtube.com/watch?v=install456 "Installation Tutorial - 10 minutes")

### Advanced Features

Learn about advanced capabilities:

[video](https://youtube.com/watch?v=advanced789 "Advanced Features Deep Dive - 25 minutes")
```

### Product Demos

```markdown
# Product Showcase

## Core Features Demo

See our platform in action:

[video](https://vimeo.com/product_demo "Live Product Demo - All Features")

## Customer Success Stories

Hear from our users:

[video](https://youtube.com/watch?v=testimonial123 "Customer Success Story - TechCorp")
[video](https://youtube.com/watch?v=testimonial456 "Case Study - StartupXYZ Growth")
```

### Training Materials

```markdown
## Developer Training

### Module 1: Authentication

[video](https://youtube.com/watch?v=auth101 "Authentication Basics - 15 min")

### Module 2: API Usage

[video](https://youtube.com/watch?v=api201 "API Best Practices - 20 min")

### Module 3: Error Handling

[video](https://youtube.com/watch?v=errors301 "Error Handling Strategies - 18 min")

## Assessment

Complete the training and take our [certification test](link).
```

## Programmatic Usage

### Creating Video Blocks

```python
from notionary.blocks.video import VideoMarkdownNode

# Simple video embed
video = VideoMarkdownNode(
    url="https://youtube.com/watch?v=dQw4w9WgXcQ",
    caption="Product Demo Video"
)

markdown = video.to_markdown()
```

### Using with Pages

```python
import asyncio
from notionary import NotionPage

async def add_training_videos():
    page = await NotionPage.from_page_name("Training Materials")

    training_content = '''
# Developer Training Program

## Introduction
Welcome to our comprehensive training program.

## Module 1: Getting Started
[video](https://youtube.com/watch?v=intro123 "Introduction - 10 minutes")

Key concepts covered:
- Platform overview
- Basic navigation
- Account setup

## Module 2: API Fundamentals
[video](https://youtube.com/watch?v=api456 "API Basics - 15 minutes")

Learn about:
- Authentication methods
- Making requests
- Handling responses
    '''

    await page.replace_content(training_content)

asyncio.run(add_training_videos())
```

### Playlist Creation

```python
def create_video_playlist(videos, title):
    content = [f"# {title}\n"]

    for i, video in enumerate(videos, 1):
        content.append(f"## Part {i}: {video['title']}")
        content.append(f'[video]({video["url"]} "{video["description"]}")')
        content.append("")  # Empty line

    return "\n".join(content)

# Usage
playlist_videos = [
    {
        "title": "Introduction",
        "url": "https://youtube.com/watch?v=intro123",
        "description": "Course overview and objectives"
    },
    {
        "title": "Setup",
        "url": "https://youtube.com/watch?v=setup456",
        "description": "Development environment setup"
    }
]

playlist_content = create_video_playlist(playlist_videos, "API Development Course")
await page.replace_content(playlist_content)
```

## Video Organization Patterns

### Course Structure

```markdown
# Complete API Course

## Prerequisites

[video](https://youtube.com/watch?v=prereq "Prerequisites Check - 5 min")

## Part 1: Fundamentals (45 min)

### Lesson 1.1: Introduction

[video](https://youtube.com/watch?v=intro "What is an API? - 10 min")

### Lesson 1.2: HTTP Basics

[video](https://youtube.com/watch?v=http "HTTP Methods - 15 min")

### Lesson 1.3: Authentication

[video](https://youtube.com/watch?v=auth "API Authentication - 20 min")

## Part 2: Practical Implementation (60 min)

### Lesson 2.1: Making Requests

[video](https://youtube.com/watch?v=requests "Your First API Call - 20 min")

### Lesson 2.2: Error Handling

[video](https://youtube.com/watch?v=errors "Handling API Errors - 20 min")

### Lesson 2.3: Best Practices

[video](https://youtube.com/watch?v=best "API Best Practices - 20 min")
```

### Feature Showcase

```markdown
# Platform Features

## Core Functionality

[video](https://vimeo.com/core_demo "Core Features Demo - 12 min")

## Advanced Features

### Data Integration

[video](https://youtube.com/watch?v=data_int "Data Integration Tutorial - 18 min")

### Automation Workflows

[video](https://youtube.com/watch?v=automation "Workflow Automation - 22 min")

### Custom Extensions

[video](https://youtube.com/watch?v=extensions "Building Extensions - 25 min")

## Use Cases

### E-commerce Integration

[video](https://youtube.com/watch?v=ecommerce "E-commerce Setup - 15 min")

### CRM Synchronization

[video](https://youtube.com/watch?v=crm_sync "CRM Integration Guide - 20 min")
```

## Best Practices

### Video Selection

```markdown
# ✅ Good - Relevant, high-quality videos

[video](https://youtube.com/watch?v=tutorial123 "Official Tutorial - HD Quality")

# ✅ Good - Clear descriptions

[video](https://vimeo.com/demo456 "Feature Demo - New Dashboard (5 min)")

# ❌ Avoid - Poor quality or irrelevant videos

[video](https://youtube.com/watch?v=random "Random video")

# ❌ Avoid - No context or description

[video](https://youtube.com/watch?v=mystery)
```

### Context and Integration

```markdown
## Implementation Guide

Before watching the video, review the [documentation](docs-link).

[video](https://youtube.com/watch?v=implementation "Implementation Walkthrough - 25 min")

After watching, try the [hands-on exercise](exercise-link).

### Key Takeaways:

- Always validate input data
- Implement proper error handling
- Use environment variables for configuration
- Test thoroughly before deployment
```

### Accessibility Considerations

```markdown
# Video Resources

## Training Materials

[video](https://youtube.com/watch?v=training123 "Complete Training Course - 45 min")

### Alternative Resources:

- 📄 [Written transcript](transcript-link)
- 📝 [Step-by-step guide](guide-link)
- 🎧 [Audio-only version](audio-link)
- 📱 [Mobile-friendly slides](slides-link)
```

## Integration with Other Blocks

### Videos with Callouts

```markdown
## Setup Tutorial

[callout](🎥 **Watch First:** Complete setup tutorial below "🎥")

[video](https://youtube.com/watch?v=setup123 "Development Setup - 15 minutes")

[callout](⚠️ **Important:** Restart your IDE after installation "⚠️")
```

### Videos in Toggles

```markdown
+++ Optional: Advanced Configuration
For advanced users who want to customize their setup:

[video](https://youtube.com/watch?v=advanced456 "Advanced Configuration - 20 min")

This covers:
- Custom middleware setup
- Performance optimization
- Security hardening
+++
```

### Videos in Columns

```markdown
::: columns
::: column

## Frontend Tutorial

[video](https://youtube.com/watch?v=frontend "React Setup - 15 min")

Learn to build the UI components.
:::
::: column

## Backend Tutorial

[video](https://youtube.com/watch?v=backend "API Development - 20 min")

Set up the server and database.
:::
:::
```

## Performance Considerations

### Loading Optimization

- Videos load as embedded players
- No impact on initial page load
- Lazy loading for better performance
- Responsive sizing automatically handled

### Mobile Experience

- Embedded videos adapt to screen size
- Touch-friendly controls
- Bandwidth-conscious loading
- Fallback to platform apps when available

## Related Blocks

- **[Image](image.md)** - For static visual content
- **[Audio](audio.md)** - For audio-only content
- **[File](file.md)** - For downloadable video files
- **[Embed](embed.md)** - For other embedded content
