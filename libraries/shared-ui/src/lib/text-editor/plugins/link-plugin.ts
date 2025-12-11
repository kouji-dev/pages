import { Injectable, inject, ViewContainerRef } from '@angular/core';
import {
  LexicalEditor,
  $getSelection,
  $isRangeSelection,
  KEY_DOWN_COMMAND,
  COMMAND_PRIORITY_HIGH,
} from 'lexical';
import { LinkNode, TOGGLE_LINK_COMMAND, $isLinkNode } from '@lexical/link';
import { TextEditorPlugin } from './plugin';
import { TextEditorService } from '../text-editor.service';
import { Modal } from '../../modal/modal';
import { LinkInputModal } from '../link-input-modal';
import { firstValueFrom } from 'rxjs';

/**
 * Link plugin for handling link operations
 */
@Injectable()
export class LinkPlugin implements TextEditorPlugin {
  private readonly editorService = inject(TextEditorService, { optional: true });
  private readonly modal = inject(Modal);
  private editor: LexicalEditor | null = null;
  private rootElement: HTMLElement | null = null;
  private viewContainerRef: ViewContainerRef | null = null;
  private unregisterListeners: (() => void)[] = [];

  register(
    editor: LexicalEditor,
    rootElement?: HTMLElement,
    viewContainerRef?: ViewContainerRef,
  ): () => void {
    this.editor = editor;
    this.rootElement = rootElement || null;
    this.viewContainerRef = viewContainerRef || null;

    // Register keyboard shortcut for link (Ctrl+K / Cmd+K)
    const unregisterLink = editor.registerCommand(
      KEY_DOWN_COMMAND,
      (event: KeyboardEvent) => {
        if (event.key === 'k' && (event.ctrlKey || event.metaKey)) {
          event.preventDefault();
          this.handleLinkFormat();
          return true;
        }
        return false;
      },
      COMMAND_PRIORITY_HIGH,
    );

    this.unregisterListeners.push(unregisterLink);

    return () => {
      this.unregisterListeners.forEach((unregister) => {
        try {
          unregister();
        } catch (error) {
          console.error('Error unregistering link plugin listener:', error);
        }
      });
      this.unregisterListeners = [];
      this.editor = null;
      this.rootElement = null;
      this.viewContainerRef = null;
    };
  }

  handleFormat(format: string): boolean {
    if (format === 'link') {
      this.insertLink();
      return true;
    }
    return false;
  }

  async insertLink(url?: string): Promise<void> {
    if (!this.editor) return;

    if (url) {
      this.toggleLink(url);
    } else {
      if (!this.viewContainerRef) {
        console.error('ViewContainerRef is required to open link modal');
        return;
      }

      const currentUrl = this.getLinkUrl() || '';
      const modal$ = this.modal.open<string | null>(LinkInputModal, this.viewContainerRef, {
        size: 'sm',
        data: { url: currentUrl },
      });

      try {
        const result = await firstValueFrom(modal$);
        if (result !== null && result !== undefined && typeof result === 'string') {
          this.toggleLink(result || null);
        }
      } catch (error) {
        // Modal was cancelled or closed
      }
    }
  }

  private handleLinkFormat(): void {
    this.insertLink();
  }

  toggleLink(url: string | null): void {
    if (this.editor) {
      this.editor.dispatchCommand(TOGGLE_LINK_COMMAND, url);
    }
  }

  isLink(): boolean {
    if (!this.editor) return false;
    let isLink = false;
    this.editor.getEditorState().read(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        const node = selection.getNodes()[0];
        isLink = $isLinkNode(node);
      }
    });
    return isLink;
  }

  getLinkUrl(): string | null {
    if (!this.editor) return null;
    let url: string | null = null;
    this.editor.getEditorState().read(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        const node = selection.getNodes()[0];
        if ($isLinkNode(node)) {
          url = node.getURL();
        }
      }
    });
    return url;
  }
}
