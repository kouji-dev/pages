import { Injectable, inject } from '@angular/core';
import { LexicalEditor, UNDO_COMMAND, REDO_COMMAND } from 'lexical';
import { createEmptyHistoryState, registerHistory } from '@lexical/history';
import { TextEditorPlugin } from './plugin';
import { TextEditorService } from '../text-editor.service';

/**
 * History plugin for undo/redo functionality
 */
@Injectable()
export class HistoryPlugin implements TextEditorPlugin {
  private readonly editorService = inject(TextEditorService, { optional: true });
  private editor: LexicalEditor | null = null;
  private rootElement: HTMLElement | null = null;
  private history: ReturnType<typeof createEmptyHistoryState> | null = null;
  private unregisterHistory: (() => void) | null = null;

  register(editor: LexicalEditor, rootElement?: HTMLElement): () => void {
    this.editor = editor;
    this.rootElement = rootElement || null;
    this.history = createEmptyHistoryState();
    this.unregisterHistory = registerHistory(editor, this.history, 300);
    return () => {
      if (this.unregisterHistory) {
        this.unregisterHistory();
        this.unregisterHistory = null;
      }
      this.editor = null;
      this.rootElement = null;
      this.history = null;
    };
  }

  undo(): void {
    if (this.editor) {
      this.editor.dispatchCommand(UNDO_COMMAND, undefined);
    }
  }

  redo(): void {
    if (this.editor) {
      this.editor.dispatchCommand(REDO_COMMAND, undefined);
    }
  }
}
