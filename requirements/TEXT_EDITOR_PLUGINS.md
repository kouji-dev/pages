# Available Lexical Plugins and Custom Elements

## Plugin Status Overview

### Core Formatting Plugins

- ✅ **Rich Text Formatting** - Bold, Italic, Underline, Strikethrough, Code
- ✅ **Headings** - H1, H2, H3
- ✅ **Lists** - Ordered and Unordered lists
- ✅ **Links** - With modal for URL input
- ✅ **Quotes** - Block quotes
- ✅ **History** - Undo/Redo
- ✅ **Font Sizes** - xs, sm, md, lg, xl
- 🔴 **Text Alignment** - Left, center, right, justify (Required for Jira/Confluence)
- 🔴 **Text Color** - Text and background color (Required for Jira/Confluence)
- 🔴 **Text Highlighting** - Highlight color (Required for Jira/Confluence)

### Content Plugins

- ✅ **Code Blocks** - CodeNode, CodeHighlightNode (registered)
- ✅ **Tables** - TableNode, TableCellNode, TableRowNode (registered)
- ✅ **Hashtags** - HashtagNode (registered)
- ✅ **Marks** - MarkNode (registered)
- 🔴 **Image Plugin** (Required for Jira/Confluence)
- 🔴 **Mention Plugin** (Required for Jira/Confluence)
- 🔴 **Checklist Plugin** (Required for Jira/Confluence)
- 🔴 **Panel/Callout Plugin** (Required for Jira/Confluence)
- 🔴 **Macro System** (Required for Jira/Confluence)
- 🔴 **Page/Issue Link Plugin** (Required for Jira/Confluence)
- 🔴 **File Attachment Plugin** (Required for Jira/Confluence)
- 🔴 **Horizontal Rule Plugin** (Required for Jira/Confluence)
- 🟡 **Enhanced Table Plugin** - Cell merging, resizing (Required for Jira/Confluence)
- 🟡 **Status Label Plugin** (Required for Jira/Confluence)
- 🟡 **Video Embed Plugin** (Required for Jira/Confluence)

### Collaboration Plugins

- 🔴 **Comment Plugin** (Required for Jira/Confluence)
- 🔴 **Real-time Collaboration Plugin** (Required for Jira/Confluence)
- 🟡 **Version History Plugin** (Required for Jira/Confluence)

### Integration Plugins

- 🔴 **Jira Integration Plugin** (Required for Jira/Confluence)
- 🟡 **Template Plugin** (Required for Jira/Confluence)

### Utility Plugins

- 🟡 **Emoji Plugin** (Required for Jira/Confluence)
- 🟡 **Date/Time Plugin** (Required for Jira/Confluence)
- 🟡 **Search & Replace Plugin** (Required for Jira/Confluence)
- 🟡 **Word Count Plugin** (Required for Jira/Confluence)
- 🟡 **Keyboard Shortcuts Plugin** (Required for Jira/Confluence)
- **AutoLink Plugin** - Automatic link detection
- **Collapsible Plugin** - Collapsible sections
- **Draggable Block Plugin** - Drag and drop blocks
- **List Max Indent Plugin** - Control list nesting depth
- **Color Plugin** - Text color picker
- **Line Height Plugin** - Adjust line spacing
- **Letter Spacing Plugin** - Character spacing
- **Font Family Plugin** - Font selection
- **Math Plugin** - LaTeX support
- **Drawing Plugin** - Freehand drawing
- **Tabs Plugin** - Tabbed content
- **Columns Plugin** - Multi-column layout
- **Spoiler Plugin** - Hidden content
- **Export Plugin** - Export to PDF/Markdown/HTML
- **Import Plugin** - Import from Markdown/HTML/DOCX
- **AI Assistant Plugin** - AI text generation
- **Accessibility Plugin** - Screen reader support

### Custom Nodes

- **Custom Block Nodes** - Custom content blocks
- **Custom Inline Nodes** - Custom inline elements
- **Custom Decorator Nodes** - Custom UI elements in editor

---

## Plugin Details

### Core Formatting Plugins

#### ✅ Rich Text Formatting

- Bold, Italic, Underline, Strikethrough, Code
- Keyboard shortcuts (Ctrl+B, Ctrl+I, Ctrl+U)
- Format state tracking

#### ✅ Headings

- H1, H2, H3 support
- Heading styles with proper sizing
- Keyboard shortcuts

#### ✅ Lists

- Ordered lists (numbered)
- Unordered lists (bulleted)
- List item nesting
- Indent/outdent support

#### ✅ Links

- URL input via modal
- Link insertion/editing
- Link removal
- Keyboard shortcut (Ctrl+K)

#### ✅ Quotes

- Block quote insertion
- Quote styling with border and italic text
- Toggle quote command

#### ✅ History

- Undo functionality
- Redo functionality
- Keyboard shortcuts (Ctrl+Z, Ctrl+Y)

#### ✅ Font Sizes

- Font size selection (xs, sm, md, lg, xl)
- Dropdown selector
- Current size detection
- Size tracking on selection changes

#### 🔴 Text Alignment (Required for Jira/Confluence)

- Left, center, right, justify alignment
- Text alignment controls
- Block alignment support

#### 🔴 Text Color (Required for Jira/Confluence)

- Text color picker
- Background color
- Color palette
- CSS color support

#### 🔴 Text Highlighting (Required for Jira/Confluence)

- Highlight color picker
- Background highlighting
- Multiple highlight colors

---

### Content Plugins

#### ✅ Code Blocks

- Code node support
- Code highlight node support
- Syntax highlighting (via CodeHighlightNode)
- Inline code formatting

#### ✅ Tables

- Table node support
- Table cell nodes
- Table row nodes
- Basic table structure

#### 🔴 Image Plugin (Required for Jira/Confluence)

- Image upload functionality
- Image resizing (drag handles)
- Image alignment (left, center, right)
- Image captions
- Image gallery view
- Image preview
- Image deletion

#### 🔴 Mention Plugin (Required for Jira/Confluence)

- User mentions (@username)
- Autocomplete dropdown
- User search/filtering
- Avatar display in mentions
- Notification triggers
- Mention node creation

#### 🔴 Checklist Plugin (Required for Jira/Confluence)

- Todo lists with checkboxes
- Task completion tracking
- Nested checklists
- Task management integration
- Checkbox state persistence

#### 🔴 Panel/Callout Plugin (Required for Jira/Confluence)

- Info panels
- Warning panels
- Note panels
- Tip panels
- Success/Error panels
- Custom panel types
- Panel icons
- Panel styling

#### 🔴 Macro System (Required for Jira/Confluence)

- Macro picker/selector
- Custom macro nodes
- Expandable macro content
- Macro configuration UI
- Common macros:
  - Table of Contents
  - Code blocks with language
  - Page embeds
  - Status labels
  - Date/time displays
  - Charts and diagrams

#### 🔴 Page/Issue Link Plugin (Required for Jira/Confluence)

- Link to other pages/documents
- Link to issues/tickets
- Autocomplete for page/issue search
- Preview on hover
- Link display with metadata
- Issue status display

#### 🔴 File Attachment Plugin (Required for Jira/Confluence)

- File upload
- File preview
- PDF viewer
- Document embedding
- Download links
- File size display
- File type icons

#### 🔴 Horizontal Rule Plugin (Required for Jira/Confluence)

- Insert dividers
- Section breaks
- Themed separators
- Horizontal rule styling

#### 🟡 Enhanced Table Plugin (Required for Jira/Confluence)

- Cell merging
- Column/row resizing
- Table alignment
- Table styles/themes
- Row/column insertion/deletion
- Table header rows
- Table footer rows

#### 🟡 Status Label Plugin (Required for Jira/Confluence)

- Status badges
- Color-coded labels
- Custom status types
- Inline status display
- Status picker

#### 🟡 Video Embed Plugin (Required for Jira/Confluence)

- YouTube embeds
- Vimeo embeds
- Video player controls
- Responsive video sizing
- Video URL parsing

---

### Collaboration Plugins

#### 🔴 Comment Plugin (Required for Jira/Confluence)

- Inline comments
- Comment threads
- Comment resolution
- @mentions in comments
- Comment notifications
- Comment avatars
- Comment timestamps

#### 🔴 Real-time Collaboration Plugin (Required for Jira/Confluence)

- Multi-user editing
- Cursor positions
- User presence indicators
- Conflict resolution
- Live updates
- User avatars
- Typing indicators

#### 🟡 Version History Plugin (Required for Jira/Confluence)

- Document versioning
- Version comparison
- Restore to previous version
- Version comments
- Change tracking
- Version diff view

---

### Integration Plugins

#### 🔴 Jira Integration Plugin (Required for Jira/Confluence)

- Create Jira issues from text
- Link to existing issues
- Display issue details inline
- Issue status updates
- Issue transitions
- Issue assignee display
- Issue priority display

#### 🟡 Template Plugin (Required for Jira/Confluence)

- Template picker
- Save as template
- Template variables
- Blueprint support
- Template categories

---

### Utility Plugins

#### 🟡 Emoji Plugin (Required for Jira/Confluence)

- Emoji picker
- Emoji autocomplete
- Emoji search
- Recent emojis
- Emoji categories

#### 🟡 Date/Time Plugin (Required for Jira/Confluence)

- Date picker
- Time picker
- Relative dates ("2 days ago")
- Timezone support
- Date formatting options

#### 🟡 Search & Replace Plugin (Required for Jira/Confluence)

- Find in editor
- Replace text
- Find next/previous
- Match case/whole word
- Replace all
- Highlight matches

#### 🟡 Word Count Plugin (Required for Jira/Confluence)

- Character count
- Word count
- Reading time estimate
- Display in toolbar
- Real-time updates

#### 🟡 Keyboard Shortcuts Plugin (Required for Jira/Confluence)

- Shortcut help modal
- Customizable shortcuts
- Markdown-style shortcuts (e.g., `**bold**`, `*italic*`)
- Slash commands (`/` for commands)
- Command palette

#### AutoLink Plugin

- Automatic link detection
- URL parsing
- Email detection
- Link conversion

#### Collapsible Plugin

- Collapsible sections
- Toggle blocks
- Accordion-style content
- Expand/collapse controls

#### Draggable Block Plugin

- Drag and drop blocks
- Reorder content
- Visual drag handles
- Drop indicators

#### List Max Indent Plugin

- Control list nesting depth
- Prevent excessive indentation
- Max indent configuration

#### Color Plugin

- Text color picker
- Background color
- Highlight color
- Color palette
- Custom color input

#### Line Height Plugin

- Adjust line spacing
- Tight, normal, relaxed, loose
- Custom line height values

#### Letter Spacing Plugin

- Character spacing
- Tracking adjustments
- Custom spacing values

#### Font Family Plugin

- Font selection
- System fonts
- Web fonts
- Monospace toggle
- Font preview

#### Math Plugin

- LaTeX support
- Math equations
- Inline math
- Block math
- Math rendering

#### Drawing Plugin

- Freehand drawing
- Shapes
- Annotations
- Drawing tools

#### Tabs Plugin

- Tabbed content
- Multi-panel content
- Tab navigation

#### Columns Plugin

- Multi-column layout
- Column widths
- Responsive columns
- Column alignment

#### Spoiler Plugin

- Hidden content
- Reveal on click
- Spoiler tags
- Spoiler styling

#### Export Plugin

- Export to PDF
- Export to Markdown
- Export to HTML
- Export to DOCX
- Export options

#### Import Plugin

- Import from Markdown
- Import from HTML
- Import from DOCX
- Paste from Word
- Import validation

#### AI Assistant Plugin

- AI text generation
- Text completion
- Grammar check
- Style suggestions
- Content improvement

#### Accessibility Plugin

- Screen reader support
- Keyboard navigation
- ARIA labels
- Focus management
- High contrast mode

---

### Custom Nodes

#### Custom Block Nodes

- Custom content blocks
- Widget nodes
- Embed nodes
- Block-level custom elements

#### Custom Inline Nodes

- Custom inline elements
- Inline widgets
- Custom formatting
- Inline-level custom elements

#### Custom Decorator Nodes

- Custom UI elements in editor
- Interactive elements
- Component embeds
- Decorator-level custom elements

---

## Integration Ideas

### CMS Integration

- Content blocks
- Media library
- Asset management

### E-commerce

- Product embeds
- Price displays
- Shopping cart

### Social Media

- Tweet embeds
- Instagram posts
- Social sharing

### Analytics

- Content analytics
- Engagement tracking
- Performance metrics

---

## Resources

- [Lexical Documentation](https://lexical.dev/)
- [Lexical Playground](https://playground.lexical.dev/)
