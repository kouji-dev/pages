import { LexicalEditor } from 'lexical';
import { ViewContainerRef } from '@angular/core';

/**
 * Base interface for all TextEditor plugins.
 * Each plugin registers itself with the editor and returns an unregister handler.
 */
export interface TextEditorPlugin {
  /**
   * Register the plugin with the provided editor.
   * @param editor The Lexical editor instance
   * @param rootElement Optional root element for keyboard shortcuts
   * @param viewContainerRef Optional view container ref for modals/dialogs
   * @returns A cleanup function to unregister the plugin.
   */
  register(
    editor: LexicalEditor,
    rootElement?: HTMLElement,
    viewContainerRef?: ViewContainerRef,
  ): () => void;

  /**
   * Handle a format action. Returns true if the format was handled.
   */
  handleFormat?(format: string): boolean;

  /**
   * Get the current format state for this plugin.
   */
  getFormatState?(): { bold: boolean; italic: boolean; underline: boolean };
}
