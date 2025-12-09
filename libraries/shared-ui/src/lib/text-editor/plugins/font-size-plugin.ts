import { Injectable, inject, ViewContainerRef, signal, effect } from '@angular/core';
import {
  LexicalEditor,
  $getSelection,
  $isRangeSelection,
  $isTextNode,
  FORMAT_TEXT_COMMAND,
  SELECTION_CHANGE_COMMAND,
  COMMAND_PRIORITY_CRITICAL,
} from 'lexical';
import { TextEditorPlugin } from './plugin';

export type FontSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

/**
 * Font size plugin for handling text size changes
 */
@Injectable()
export class FontSizePlugin implements TextEditorPlugin {
  private editor: LexicalEditor | null = null;
  private rootElement: HTMLElement | null = null;
  private unregisterListeners: (() => void)[] = [];

  // Signal to track current font size
  readonly currentFontSize = signal<FontSize | null>(null);

  register(
    editor: LexicalEditor,
    rootElement?: HTMLElement,
    viewContainerRef?: ViewContainerRef,
  ): () => void {
    this.editor = editor;
    this.rootElement = rootElement || null;

    // Listen to selection changes to update current font size
    const unregisterSelection = editor.registerCommand(
      SELECTION_CHANGE_COMMAND,
      () => {
        this.updateCurrentFontSize();
        return false;
      },
      COMMAND_PRIORITY_CRITICAL,
    );

    this.unregisterListeners.push(unregisterSelection);

    // Initial update
    this.updateCurrentFontSize();

    return () => {
      this.unregisterListeners.forEach((unregister) => {
        try {
          unregister();
        } catch (error) {
          console.error('Error unregistering font size plugin listener:', error);
        }
      });
      this.unregisterListeners = [];
      this.editor = null;
      this.rootElement = null;
      this.currentFontSize.set(null);
    };
  }

  handleFormat(format: string): boolean {
    const sizes: FontSize[] = ['xs', 'sm', 'md', 'lg', 'xl'];
    if (sizes.includes(format as FontSize)) {
      this.setFontSize(format as FontSize);
      return true;
    }
    return false;
  }

  setFontSize(size: FontSize): void {
    if (!this.editor) return;

    this.editor.update(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        const nodes = selection.getNodes();
        nodes.forEach((node) => {
          if ($isTextNode(node)) {
            node.setStyle(`font-size: var(--text-${size})`);
          }
        });
      }
    });

    // Update current font size after setting
    this.updateCurrentFontSize();
  }

  removeFontSize(): void {
    if (!this.editor) return;

    this.editor.update(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        const nodes = selection.getNodes();
        nodes.forEach((node) => {
          if ($isTextNode(node)) {
            const style = node.getStyle();
            // Remove font-size from style
            const newStyle = style
              .split(';')
              .filter((prop) => !prop.trim().startsWith('font-size:'))
              .join(';')
              .trim();
            node.setStyle(newStyle || '');
          }
        });
      }
    });

    // Update current font size after removing
    this.updateCurrentFontSize();
  }

  private updateCurrentFontSize(): void {
    if (!this.editor) {
      this.currentFontSize.set(null);
      return;
    }

    let fontSize: FontSize | null = null;
    this.editor.getEditorState().read(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        const nodes = selection.getNodes();
        if (nodes.length > 0) {
          const firstNode = nodes[0];
          if ($isTextNode(firstNode)) {
            const style = firstNode.getStyle();
            const match = style.match(/font-size:\s*var\(--text-(\w+)\)/);
            if (match) {
              fontSize = match[1] as FontSize;
            }
          }
        }
      }
    });
    this.currentFontSize.set(fontSize);
  }

  getFontSize(): FontSize | null {
    return this.currentFontSize();
  }
}
