import { Injectable, inject, ViewContainerRef } from '@angular/core';
import { LexicalEditor, $getSelection, $insertNodes, $createParagraphNode } from 'lexical';
import { TextEditorPlugin } from './plugin';
import { TextEditorService } from '../text-editor.service';
import { $createImageNode } from '../nodes/image-node';

/**
 * Plugin for handling image insertion
 */
@Injectable()
export class ImagePlugin implements TextEditorPlugin {
  private readonly editorService = inject(TextEditorService, { optional: true });
  private editor: LexicalEditor | null = null;
  private rootElement: HTMLElement | null = null;
  private viewContainerRef: ViewContainerRef | null = null;

  register(
    editor: LexicalEditor,
    rootElement?: HTMLElement,
    viewContainerRef?: ViewContainerRef,
  ): () => void {
    this.editor = editor;
    this.rootElement = rootElement || null;
    this.viewContainerRef = viewContainerRef || null;

    return () => {
      this.editor = null;
      this.rootElement = null;
      this.viewContainerRef = null;
    };
  }

  /**
   * Insert an image node at the current selection or cursor position
   * @param src Image source URL
   * @param alt Alt text
   * @param width Optional width
   * @param height Optional height
   */
  insertImage(src: string, alt: string = '', width?: number, height?: number): void {
    if (!this.editor) return;

    this.editor.update(() => {
      const selection = $getSelection();
      if (selection) {
        const imageNode = $createImageNode({ src, alt, width, height });
        $insertNodes([imageNode]);
        // Insert a paragraph after the image for better UX
        const paragraph = $createParagraphNode();
        $insertNodes([paragraph]);
      }
    });
  }

  /**
   * Insert an image from a file input
   */
  async insertImageFromFile(file: File): Promise<void> {
    // For demo purposes, create a data URL
    // In production, you would upload the file and get a URL
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const src = e.target?.result as string;
        if (src) {
          this.insertImage(src, file.name);
          resolve();
        } else {
          reject(new Error('Failed to read file'));
        }
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
}
