# Image Naming Conventions

## Overview

This document defines the naming conventions for all screenshots and demo assets in HireFlow AI.

## General Rules

### Format

- Use **kebab-case** (lowercase with hyphens)
- No spaces or underscores
- Descriptive and meaningful names
- Consistent across all assets

### Structure

```
[feature-name]-[sequence-number]-[description].[extension]
```

### Examples

- `dashboard-01-main-view.png`
- `resume-parser-02-upload-interface.png`
- `job-matcher-03-match-results.png`

## Feature-Specific Conventions

### Dashboard

```
dashboard-[sequence]-[description].png
```

Examples:
- `dashboard-01-main-view.png`
- `dashboard-02-navigation.png`
- `dashboard-03-overview.png`

### Resume Parser

```
resume-parser-[sequence]-[description].png
```

Examples:
- `resume-parser-01-upload.png`
- `resume-parser-02-parsing.png`
- `resume-parser-03-results.png`
- `resume-parser-04-skills.png`

### Job Matcher

```
job-matcher-[sequence]-[description].png
```

Examples:
- `job-matcher-01-selection.png`
- `job-matcher-02-analysis.png`
- `job-matcher-03-results.png`
- `job-matcher-04-charts.png`

### Job Discovery

```
job-discovery-[sequence]-[description].png
```

Examples:
- `job-discovery-01-search.png`
- `job-discovery-02-results.png`
- `job-discovery-03-filters.png`
- `job-discovery-04-details.png`

### Career Coach

```
career-coach-[sequence]-[description].png
```

Examples:
- `career-coach-01-question.png`
- `career-coach-02-response.png`
- `career-coach-03-advice.png`

### Analytics

```
analytics-[sequence]-[description].png
```

Examples:
- `analytics-01-overview.png`
- `analytics-02-charts.png`
- `analytics-03-metrics.png`
- `analytics-04-trends.png`

### Application Tracker

```
application-tracker-[sequence]-[description].png
```

Examples:
- `application-tracker-01-list.png`
- `application-tracker-02-details.png`
- `application-tracker-03-status.png`

## Description Guidelines

### Use Action Verbs

- `upload` instead of `file-upload`
- `analyze` instead of `analysis`
- `search` instead of `searching`

### Be Specific

- `upload-interface` instead of `screen`
- `match-results` instead of `output`
- `skill-analysis` instead of `skills`

### Keep It Short

- Maximum 3-4 words in description
- Prefer shorter, clearer names
- Avoid unnecessary words

## Sequence Numbers

### Numbering System

- Use 2-digit numbers (01, 02, 03)
- Start from 01 for each feature
- Increment sequentially
- Leave gaps for future additions

### Examples

```
resume-parser-01-upload.png
resume-parser-02-parsing.png
resume-parser-03-results.png
```

## File Extensions

### Images

- **PNG**: Screenshots with text (preferred)
- **JPG**: Photographs or complex images
- **WebP**: Web-optimized images

### Videos

- **MP4**: Video recordings
- **GIF**: Animated demonstrations
- **WEBM**: Web-optimized video

## Version Control

### Version Numbers

When updating screenshots:

```
[feature-name]-[sequence]-[description]-v[version].png
```

Examples:
- `dashboard-01-main-view-v2.png`
- `resume-parser-01-upload-v1.png`

### Date Stamps (Optional)

For time-sensitive content:

```
[feature-name]-[sequence]-[description]-[YYYY-MM-DD].png
```

Examples:
- `dashboard-01-main-view-2024-06-20.png`

## Folder Structure

### Organize by Feature

```
screenshots/
├── dashboard/
│   ├── dashboard-01-main-view.png
│   ├── dashboard-02-navigation.png
│   └── dashboard-03-overview.png
├── resume-parser/
│   ├── resume-parser-01-upload.png
│   ├── resume-parser-02-parsing.png
│   └── resume-parser-03-results.png
└── job-matcher/
    ├── job-matcher-01-selection.png
    ├── job-matcher-02-analysis.png
    └── job-matcher-03-results.png
```

## Special Cases

### Mobile Screenshots

```
mobile-[feature]-[sequence]-[description].png
```

Examples:
- `mobile-dashboard-01-main-view.png`
- `mobile-resume-parser-01-upload.png`

### Dark Mode

```
[feature]-[sequence]-[description]-dark-mode.png
```

Examples:
- `dashboard-01-main-view-dark-mode.png`

### Error States

```
[feature]-[sequence]-[description]-error.png
```

Examples:
- `resume-parser-01-upload-error.png`

## File Size Guidelines

### Target Sizes

- **PNG**: Under 500KB (screenshots)
- **JPG**: Under 300KB (photos)
- **GIF**: Under 2MB (animations)
- **MP4**: Under 10MB (short videos)

### Optimization

- Use image compression tools
- Reduce color depth where possible
- Remove metadata
- Use appropriate format

## Metadata

### EXIF Data

Remove sensitive metadata:
- GPS location
- Camera information
- Timestamp
- Device information

### Tools

- **ExifTool**: Remove metadata
- **ImageOptim**: Mac optimizer
- **FileOptimizer**: Windows optimizer

## Validation

### Checklist

Before committing screenshots:

- [ ] Follows naming convention
- [ ] Appropriate file extension
- [ ] Under size limit
- [ ] No personal data visible
- [ ] Good image quality
- [ ] Descriptive name
- [ ] In correct folder
- [ ] Metadata removed

## Examples

### Good Names

- `dashboard-01-main-view.png` ✓
- `resume-parser-02-upload-interface.png` ✓
- `job-matcher-03-match-results.png` ✓

### Bad Names

- `Screenshot 1.png` ✗
- `image.jpg` ✗
- `Dashboard_Screenshot.png` ✗
- `resume parser upload.png` ✗

## Migration Guide

### Renaming Existing Files

If you have files that don't follow conventions:

1. Identify files to rename
2. Apply new naming convention
3. Update references in documentation
4. Commit changes with descriptive message

### Bulk Renaming

```bash
# Example: Rename all files in a folder
for file in *.png; do
  mv "$file" "${file// /-}"
done
```

## Documentation Updates

### Update References

When renaming files:

1. Search for old filenames in docs
2. Update README.md
3. Update documentation files
4. Test all links
5. Commit changes

---

**Last Updated**: June 20, 2026  
**Maintained By**: Jayesh
