import { Injectable, signal, ViewContainerRef } from '@angular/core';
import {
  LexicalEditor,
  createEditor,
  $getRoot,
  RootNode,
  ParagraphNode,
  TextNode,
  SerializedEditorState,
  SerializedLexicalNode,
} from 'lexical';
import { $generateNodesFromDOM, $generateHtmlFromNodes } from '@lexical/html';
import { HeadingNode, QuoteNode } from '@lexical/rich-text';
import { ListNode, ListItemNode } from '@lexical/list';
import { LinkNode } from '@lexical/link';
import { TableNode, TableCellNode, TableRowNode } from '@lexical/table';
import { CodeNode, CodeHighlightNode } from '@lexical/code';
import { HashtagNode } from '@lexical/hashtag';
import { MarkNode } from '@lexical/mark';
import { TextEditorPlugin } from './plugins/plugin';
import { HistoryPlugin } from './plugins/history-plugin';
import { ListPlugin } from './plugins/list-plugin';
import { LinkPlugin } from './plugins/link-plugin';
import { RichTextPlugin } from './plugins/rich-text-plugin';
import { HeadingPlugin } from './plugins/heading-plugin';
import { AttachmentNode } from './nodes/attachment-node';
import { ImageNode } from './nodes/image-node';
import { MentionNode } from './nodes/mention-node';

/**
 * Service that holds the current LexicalEditor instance.
 * Provided at component level for each text editor instance.
 */
@Injectable()
export class TextEditorService {
  private readonly _editor = signal<LexicalEditor | null>(null);
  private unregisterListeners: (() => void)[] = [];
  private pluginRegistrations: Array<{ plugin: TextEditorPlugin; unregister: () => void }> = [];

  /**
   * Get the current editor instance
   */
  get editor(): LexicalEditor | null {
    return this._editor();
  }

  /**
   * Create and initialize the editor
   * If an editor already exists, it will be destroyed first
   */
  createEditor(
    plugins: TextEditorPlugin[],
    initialValue?: string,
    onUpdate?: (html: string, text: string) => void,
    viewContainerRef?: ViewContainerRef,
  ): LexicalEditor {
    // Cleanup existing editor if it exists
    if (this.hasEditor()) {
      this.destroy();
    }

    // Initialize Lexical editor
    const editor = createEditor({
      editable: true,
      nodes: [
        // Core nodes
        RootNode,
        ParagraphNode,
        TextNode,
        // Rich text nodes
        HeadingNode,
        QuoteNode,
        // List nodes
        ListNode,
        ListItemNode,
        // Link node
        LinkNode,
        // Table nodes
        TableNode,
        TableCellNode,
        TableRowNode,
        // Code nodes
        CodeNode,
        CodeHighlightNode,
        // Hashtag node
        HashtagNode,
        // Mark node
        MarkNode,
        // Custom nodes
        AttachmentNode,
        ImageNode,
        MentionNode,
      ],
      onError: (error: Error) => {
        console.error('Lexical editor error:', error);
      },
      theme: {
        paragraph: 'te-paragraph',
        heading: {
          h1: 'te-h1',
          h2: 'te-h2',
          h3: 'te-h3',
        },
        list: {
          ul: 'te-ul',
          ol: 'te-ol',
          listitem: 'te-li',
        },
        link: 'te-link',
        text: {
          bold: 'te-bold',
          italic: 'te-italic',
          underline: 'te-underline',
          strikethrough: 'te-strikethrough',
          code: 'te-code',
        },
        quote: 'te-quote',
      },
    });

    // Store editor first
    this._editor.set(editor);

    // Set initial value if provided
    if (initialValue) {
      editor.update(() => {
        const root = $getRoot();
        root.clear();
        const parser = new DOMParser();
        const dom = parser.parseFromString(initialValue, 'text/html');
        const nodes = $generateNodesFromDOM(editor, dom);
        root.append(...nodes);
      });
    }

    // Register all plugins
    this.registerPlugins(plugins, editor, viewContainerRef);

    // Register update listener for content changes
    if (onUpdate) {
      const unregisterUpdate = editor.registerUpdateListener(({ editorState }) => {
        editorState.read(() => {
          const htmlString = $generateHtmlFromNodes(editor, null);
          const textContent = $getRoot().getTextContent();
          onUpdate(htmlString, textContent);
        });
      });
      this.unregisterListeners.push(unregisterUpdate);
    }

    return editor;
  }

  /**
   * Set the root element for the editor
   * Should be called in AfterViewInit
   */
  setRootElement(rootElement: HTMLElement): void {
    const editor = this._editor();
    if (!editor) {
      throw new Error('Editor must be created before setting root element');
    }
    editor.setRootElement(rootElement);
    editor.setEditable(true);
  }

  /**
   * Register all plugins with the editor
   */
  private registerPlugins(
    plugins: TextEditorPlugin[],
    editor: LexicalEditor,
    viewContainerRef?: ViewContainerRef,
  ): void {
    this.pluginRegistrations = plugins.map((plugin) => ({
      plugin,
      unregister: plugin.register(editor, undefined, viewContainerRef),
    }));
  }

  /**
   * Handle a format action by delegating to plugins
   */
  handleFormat(format: string): boolean {
    for (const { plugin } of this.pluginRegistrations) {
      if (plugin.handleFormat && plugin.handleFormat(format)) {
        return true;
      }
    }
    return false;
  }

  /**
   * Get a specific plugin by type
   */
  getHistoryPlugin(): HistoryPlugin | null {
    const plugin = this.pluginRegistrations.find((r) => r.plugin instanceof HistoryPlugin)?.plugin;
    return plugin instanceof HistoryPlugin ? plugin : null;
  }

  getListPlugin(): ListPlugin | null {
    const plugin = this.pluginRegistrations.find((r) => r.plugin instanceof ListPlugin)?.plugin;
    return plugin instanceof ListPlugin ? plugin : null;
  }

  getLinkPlugin(): LinkPlugin | null {
    const plugin = this.pluginRegistrations.find((r) => r.plugin instanceof LinkPlugin)?.plugin;
    return plugin instanceof LinkPlugin ? plugin : null;
  }

  getRichTextPlugin(): RichTextPlugin | null {
    const plugin = this.pluginRegistrations.find((r) => r.plugin instanceof RichTextPlugin)?.plugin;
    return plugin instanceof RichTextPlugin ? plugin : null;
  }

  getHeadingPlugin(): HeadingPlugin | null {
    const plugin = this.pluginRegistrations.find((r) => r.plugin instanceof HeadingPlugin)?.plugin;
    return plugin instanceof HeadingPlugin ? plugin : null;
  }

  /**
   * Check if editor is initialized
   */
  hasEditor(): boolean {
    return this._editor() !== null;
  }

  /**
   * Get editor state as JSON
   */
  getJSON(): SerializedEditorState<SerializedLexicalNode> | null {
    const editor = this._editor();
    if (!editor) return null;
    return editor.getEditorState().toJSON();
  }

  /**
   * Set editor state from JSON
   */
  setJSON(json: SerializedEditorState<SerializedLexicalNode>): void {
    const editor = this._editor();
    if (!editor) return;
    const editorState = editor.parseEditorState(json);
    editor.setEditorState(editorState);
  }

  /**
   * Cleanup the editor and all listeners
   */
  destroy(): void {
    // Unregister all plugins
    this.pluginRegistrations.forEach(({ unregister }) => {
      try {
        unregister();
      } catch (error) {
        console.error('Error unregistering plugin:', error);
      }
    });
    this.pluginRegistrations = [];

    // Unregister all listeners
    this.unregisterListeners.forEach((unregister) => {
      try {
        unregister();
      } catch (error) {
        console.error('Error unregistering listener:', error);
      }
    });
    this.unregisterListeners = [];

    // Clean up editor
    const editor = this._editor();
    if (editor) {
      // Don't remove the root element from DOM - just unset it
      // The container element should remain in the DOM
      editor.setRootElement(null);
      this._editor.set(null);
    }
  }
}
