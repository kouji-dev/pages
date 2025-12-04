# Design Inspiration

This folder contains design reference images and inspiration for the Pages application.

## Design Philosophy

Our design system combines elements from:

- **Notion**: Clean, text-first interface with subtle colors and generous spacing
- **Jira/Confluence**: Structured layouts, clear information hierarchy, and functional UI patterns

## Color Preference

**Notion's color palette is preferred** as the primary color system, while maintaining Jira/Confluence's organizational structure and UI patterns.

## Design References

### Notion Home Page

- `notion home page.png`: Reference for Notion's homepage layout, typography, and spacing
- Key inspiration: Clean sidebar navigation, minimalist design, text-first approach

## Design Tokens

Design tokens are defined in `libraries/shared-ui/src/styles.css` using Tailwind CSS 4's CSS custom properties approach.

### Key Design Principles from References:

1. **Text-First**: Like Notion, prioritize text content with generous spacing
2. **Subtle Colors**: Use Notion's muted color palette for backgrounds and accents
3. **Clear Hierarchy**: Maintain Jira/Confluence's structured information presentation
4. **Minimal Shadows**: Subtle shadows for depth without distraction
5. **Generous Spacing**: Comfortable reading experience with ample whitespace

## Usage

When implementing new components or features:

1. Reference the design images in this folder for visual inspiration
2. Use design tokens from `shared-ui/src/styles.css`
3. Follow BOM (Block Object Modifier) CSS methodology
4. Ensure mobile responsiveness
5. Maintain accessibility standards

---

_Last Updated: December 2024_
