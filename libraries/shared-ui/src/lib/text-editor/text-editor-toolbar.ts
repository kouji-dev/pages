import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { ToolbarBoldButton } from './toolbar/toolbar-bold-button';
import { ToolbarItalicButton } from './toolbar/toolbar-italic-button';
import { ToolbarUnderlineButton } from './toolbar/toolbar-underline-button';
import { ToolbarStrikethroughButton } from './toolbar/toolbar-strikethrough-button';
import { ToolbarCodeButton } from './toolbar/toolbar-code-button';
import { ToolbarHeadingButton } from './toolbar/toolbar-heading-button';
import { ToolbarListButton } from './toolbar/toolbar-list-button';
import { ToolbarLinkButton } from './toolbar/toolbar-link-button';
import { ToolbarQuoteButton } from './toolbar/toolbar-quote-button';
import { ToolbarUndoButton } from './toolbar/toolbar-undo-button';
import { ToolbarRedoButton } from './toolbar/toolbar-redo-button';
import { ToolbarFontSizeSelect } from './toolbar/toolbar-font-size-select';
import { ToolbarAttachmentButton } from './toolbar/toolbar-attachment-button';
import { ToolbarImageButton } from './toolbar/toolbar-image-button';

@Component({
  selector: 'lib-text-editor-toolbar',
  imports: [
    ToolbarBoldButton,
    ToolbarItalicButton,
    ToolbarUnderlineButton,
    ToolbarStrikethroughButton,
    ToolbarCodeButton,
    ToolbarHeadingButton,
    ToolbarListButton,
    ToolbarLinkButton,
    ToolbarQuoteButton,
    ToolbarUndoButton,
    ToolbarRedoButton,
    ToolbarFontSizeSelect,
    ToolbarAttachmentButton,
    ToolbarImageButton,
  ],
  template: `
    @if (showToolbar()) {
      <div class="text-editor_toolbar">
        <div class="text-editor_toolbar-group">
          <lib-toolbar-bold-button />
          <lib-toolbar-italic-button />
          <lib-toolbar-underline-button />
          <lib-toolbar-strikethrough-button />
          <lib-toolbar-code-button />
        </div>
        <div class="text-editor_toolbar-separator"></div>
        <div class="text-editor_toolbar-group">
          <lib-toolbar-heading-button [tag]="'h1'" />
          <lib-toolbar-heading-button [tag]="'h2'" />
          <lib-toolbar-heading-button [tag]="'h3'" />
        </div>
        <div class="text-editor_toolbar-separator"></div>
        <div class="text-editor_toolbar-group">
          <lib-toolbar-list-button [type]="'ul'" />
          <lib-toolbar-list-button [type]="'ol'" />
        </div>
        <div class="text-editor_toolbar-separator"></div>
        <div class="text-editor_toolbar-group">
          <lib-toolbar-quote-button />
          <lib-toolbar-link-button />
          <lib-toolbar-image-button />
          <lib-toolbar-attachment-button />
        </div>
        <div class="text-editor_toolbar-separator"></div>
        <div class="text-editor_toolbar-group">
          <lib-toolbar-font-size-select />
        </div>
        <div class="text-editor_toolbar-separator"></div>
        <div class="text-editor_toolbar-group">
          <lib-toolbar-undo-button />
          <lib-toolbar-redo-button />
        </div>
      </div>
    }
  `,
  styles: [
    `
      @reference "#theme";

      .text-editor_toolbar {
        @apply flex items-center gap-1;
        @apply p-2;
        @apply border-b border-border;
        @apply bg-muted/40;
        @apply flex-wrap;
      }

      .text-editor_toolbar-group {
        @apply flex items-center gap-1;
      }

      .text-editor_toolbar-separator {
        @apply w-px h-6;
        @apply bg-border;
        @apply mx-1;
      }

      .text-editor_toolbar-button--active {
        @apply bg-primary/10;
        @apply border-primary/20;
        @apply text-primary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TextEditorToolbar {
  readonly showToolbar = input<boolean>(true);
}
