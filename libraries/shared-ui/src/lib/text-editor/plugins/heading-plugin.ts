import { Injectable, inject } from '@angular/core';
import { LexicalEditor, $getSelection, $isRangeSelection } from 'lexical';
import {
  HeadingNode,
  $createHeadingNode,
  HeadingTagType,
  $isHeadingNode,
} from '@lexical/rich-text';
import { TextEditorPlugin } from './plugin';
import { TextEditorService } from '../text-editor.service';

/**
 * Heading plugin for handling heading operations
 */
@Injectable()
export class HeadingPlugin implements TextEditorPlugin {
  private readonly editorService = inject(TextEditorService, { optional: true });
  private editor: LexicalEditor | null = null;
  private rootElement: HTMLElement | null = null;

  register(editor: LexicalEditor, rootElement?: HTMLElement): () => void {
    this.editor = editor;
    this.rootElement = rootElement || null;
    return () => {
      this.editor = null;
      this.rootElement = null;
    };
  }

  handleFormat(format: string): boolean {
    if (
      format === 'h1' ||
      format === 'h2' ||
      format === 'h3' ||
      format === 'h4' ||
      format === 'h5' ||
      format === 'h6'
    ) {
      this.insertHeading(format as HeadingTagType);
      return true;
    }
    return false;
  }

  insertHeading(tag: HeadingTagType): void {
    if (!this.editor) return;

    this.editor.update(() => {
      const selection = $getSelection();
      if (!$isRangeSelection(selection)) {
        return;
      }

      const nodes = selection.getNodes();
      const firstNode = nodes[0];
      if ($isHeadingNode(firstNode)) {
        firstNode.replace($createHeadingNode(tag));
      } else {
        const heading = $createHeadingNode(tag);
        selection.insertNodes([heading]);
      }
    });
  }
}
