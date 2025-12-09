import { Injectable, inject } from '@angular/core';
import {
  LexicalEditor,
  $getSelection,
  $isRangeSelection,
  FORMAT_TEXT_COMMAND,
  FORMAT_ELEMENT_COMMAND,
  KEY_DOWN_COMMAND,
  COMMAND_PRIORITY_HIGH,
  SELECTION_CHANGE_COMMAND,
  COMMAND_PRIORITY_CRITICAL,
} from 'lexical';
import { registerRichText, QuoteNode, $createQuoteNode, $isQuoteNode } from '@lexical/rich-text';
import { TextEditorPlugin } from './plugin';
import { TextEditorService } from '../text-editor.service';

/**
 * Rich text plugin for handling text formatting
 */
@Injectable()
export class RichTextPlugin implements TextEditorPlugin {
  private readonly editorService = inject(TextEditorService, { optional: true });
  private editor: LexicalEditor | null = null;
  private rootElement: HTMLElement | null = null;
  private unregisterListeners: (() => void)[] = [];
  private unregisterRichText: (() => void) | null = null;

  register(editor: LexicalEditor, rootElement?: HTMLElement): () => void {
    this.editor = editor;
    this.rootElement = rootElement || null;

    this.unregisterRichText = registerRichText(editor);

    // Register keyboard shortcuts
    const unregisterBold = editor.registerCommand(
      KEY_DOWN_COMMAND,
      (event: KeyboardEvent) => {
        if (event.key === 'b' && (event.ctrlKey || event.metaKey)) {
          event.preventDefault();
          this.formatText('bold');
          return true;
        }
        return false;
      },
      COMMAND_PRIORITY_HIGH,
    );

    const unregisterItalic = editor.registerCommand(
      KEY_DOWN_COMMAND,
      (event: KeyboardEvent) => {
        if (event.key === 'i' && (event.ctrlKey || event.metaKey)) {
          event.preventDefault();
          this.formatText('italic');
          return true;
        }
        return false;
      },
      COMMAND_PRIORITY_HIGH,
    );

    const unregisterUnderline = editor.registerCommand(
      KEY_DOWN_COMMAND,
      (event: KeyboardEvent) => {
        if (event.key === 'u' && (event.ctrlKey || event.metaKey)) {
          event.preventDefault();
          this.formatText('underline');
          return true;
        }
        return false;
      },
      COMMAND_PRIORITY_HIGH,
    );

    // Register selection change listener for format state
    const unregisterSelection = editor.registerCommand(
      SELECTION_CHANGE_COMMAND,
      () => {
        this.updateFormatState();
        return false;
      },
      COMMAND_PRIORITY_CRITICAL,
    );

    this.unregisterListeners.push(unregisterBold, unregisterItalic, unregisterUnderline, () =>
      unregisterSelection(),
    );

    // Initial format state update
    this.updateFormatState();

    return () => {
      if (this.unregisterRichText) {
        this.unregisterRichText();
        this.unregisterRichText = null;
      }
      this.unregisterListeners.forEach((unregister) => {
        try {
          unregister();
        } catch (error) {
          console.error('Error unregistering rich text plugin listener:', error);
        }
      });
      this.unregisterListeners = [];
      this.editor = null;
      this.rootElement = null;
    };
  }

  handleFormat(format: string): boolean {
    if (
      format === 'bold' ||
      format === 'italic' ||
      format === 'underline' ||
      format === 'strikethrough' ||
      format === 'code'
    ) {
      this.format(format as 'bold' | 'italic' | 'underline' | 'strikethrough' | 'code');
      return true;
    }
    if (format === 'quote') {
      this.insertQuote();
      return true;
    }
    return false;
  }

  insertQuote(): void {
    if (!this.editor) return;

    this.editor.update(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        const quote = $createQuoteNode();
        selection.insertNodes([quote]);
      }
    });
  }

  getFormatState(): { bold: boolean; italic: boolean; underline: boolean } {
    if (!this.editor) {
      return { bold: false, italic: false, underline: false };
    }

    let state = { bold: false, italic: false, underline: false };
    this.editor.getEditorState().read(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        state = {
          bold: selection.hasFormat('bold'),
          italic: selection.hasFormat('italic'),
          underline: selection.hasFormat('underline'),
        };
      }
    });
    return state;
  }

  private updateFormatState(): void {
    // Format state tracking removed - can be added back if needed
  }

  format(format: 'bold' | 'italic' | 'underline' | 'strikethrough' | 'code'): void {
    if (this.editor) {
      this.editor.update(() => {
        const selection = $getSelection();
        if ($isRangeSelection(selection)) {
          this.editor!.dispatchCommand(FORMAT_TEXT_COMMAND, format);
        }
      });
      this.updateFormatState();
    }
  }

  formatText(format: 'bold' | 'italic' | 'underline' | 'strikethrough' | 'code'): void {
    this.format(format);
  }

  formatElement(format: 'left' | 'center' | 'right' | 'justify'): void {
    if (this.editor) {
      this.editor.dispatchCommand(FORMAT_ELEMENT_COMMAND, format);
    }
  }

  hasFormat(format: 'bold' | 'italic' | 'underline' | 'strikethrough' | 'code'): boolean {
    if (!this.editor) return false;
    let hasFormat = false;
    this.editor.getEditorState().read(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        hasFormat = selection.hasFormat(format);
      }
    });
    return hasFormat;
  }
}
