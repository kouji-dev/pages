import { Injectable, inject, ViewContainerRef } from '@angular/core';
import { LexicalEditor, INDENT_CONTENT_COMMAND, OUTDENT_CONTENT_COMMAND } from 'lexical';
import {
  INSERT_UNORDERED_LIST_COMMAND,
  INSERT_ORDERED_LIST_COMMAND,
  REMOVE_LIST_COMMAND,
  registerList,
  ListNode,
  ListItemNode,
} from '@lexical/list';
import { TextEditorPlugin } from './plugin';
import { TextEditorService } from '../text-editor.service';

/**
 * List plugin for handling list operations
 */
@Injectable()
export class ListPlugin implements TextEditorPlugin {
  private readonly editorService = inject(TextEditorService, { optional: true });
  private editor: LexicalEditor | null = null;
  private rootElement: HTMLElement | null = null;
  private unregisterList: (() => void) | null = null;

  register(
    editor: LexicalEditor,
    rootElement?: HTMLElement,
    viewContainerRef?: ViewContainerRef,
  ): () => void {
    this.editor = editor;
    this.rootElement = rootElement || null;

    // Verify that ListNode and ListItemNode are registered
    if (!editor.hasNodes([ListNode, ListItemNode])) {
      throw new Error('ListPlugin: ListNode and/or ListItemNode not registered on editor');
    }

    // Register list functionality (handles list transformations, keyboard shortcuts, etc.)
    this.unregisterList = registerList(editor);

    return () => {
      if (this.unregisterList) {
        this.unregisterList();
        this.unregisterList = null;
      }
      this.editor = null;
      this.rootElement = null;
    };
  }

  handleFormat(format: string): boolean {
    if (format === 'ul') {
      this.insertUnorderedList();
      return true;
    } else if (format === 'ol') {
      this.insertOrderedList();
      return true;
    }
    return false;
  }

  insertUnorderedList(): void {
    if (this.editor) {
      this.editor.dispatchCommand(INSERT_UNORDERED_LIST_COMMAND, undefined);
    }
  }

  insertOrderedList(): void {
    if (this.editor) {
      this.editor.dispatchCommand(INSERT_ORDERED_LIST_COMMAND, undefined);
    }
  }

  insertList(type: 'ul' | 'ol'): void {
    if (type === 'ul') {
      this.insertUnorderedList();
    } else {
      this.insertOrderedList();
    }
  }

  removeList(): void {
    if (this.editor) {
      this.editor.dispatchCommand(REMOVE_LIST_COMMAND, undefined);
    }
  }

  indent(): void {
    if (this.editor) {
      this.editor.dispatchCommand(INDENT_CONTENT_COMMAND, undefined);
    }
  }

  outdent(): void {
    if (this.editor) {
      this.editor.dispatchCommand(OUTDENT_CONTENT_COMMAND, undefined);
    }
  }
}
