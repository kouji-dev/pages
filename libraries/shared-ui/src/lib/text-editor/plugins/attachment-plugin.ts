import { Injectable, inject, ViewContainerRef } from '@angular/core';
import { LexicalEditor, $getSelection, $insertNodes, $createParagraphNode } from 'lexical';
import { TextEditorPlugin } from './plugin';
import { TextEditorService } from '../text-editor.service';
import { $createAttachmentNode } from '../nodes/attachment-node';
import { injectAttachmentService } from '../interfaces/attachment-service.interface';

/**
 * Plugin for handling attachment insertion
 */
@Injectable()
export class AttachmentPlugin implements TextEditorPlugin {
  private readonly editorService = inject(TextEditorService, { optional: true });
  private readonly attachmentService = injectAttachmentService();
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
   * Insert an attachment node at the current selection or cursor position
   */
  insertAttachment(attachmentId?: string): void {
    if (!this.editor) return;

    const id = attachmentId || this.attachmentService.getNextId();

    this.editor.update(() => {
      const selection = $getSelection();
      if (selection) {
        const attachmentNode = $createAttachmentNode({ attachmentId: id });
        $insertNodes([attachmentNode]);
        // Insert a paragraph after the attachment for better UX
        const paragraph = $createParagraphNode();
        $insertNodes([paragraph]);
      }
    });
  }

  /**
   * Insert an attachment from a file input
   */
  async insertAttachmentFromFile(file: File): Promise<void> {
    if (!this.editor) return;

    try {
      // Upload the file and get the attachment ID
      const id = await this.attachmentService.upload(file);
      this.insertAttachment(id);
    } catch (error) {
      console.error('Failed to upload attachment:', error);
      // Optionally show an error message to the user
    }
  }
}
