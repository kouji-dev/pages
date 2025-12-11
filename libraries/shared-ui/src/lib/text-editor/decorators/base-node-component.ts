import { Directive, inject, Injector, InjectionToken, signal, computed } from '@angular/core';
import { DecoratorNode, LexicalNode, $getNodeByKey } from 'lexical';
import { TextEditorService } from '../text-editor.service';

/**
 * Injection token for the Lexical node key
 */
export const NODE_KEY = new InjectionToken<string>('NODE_KEY');

/**
 * Base component for all Lexical decorator nodes
 * Provides access to the node key and editor service via dependency injection
 *
 * @template T - The specific DecoratorNode type this component represents
 */
@Directive()
export abstract class BaseNodeComponent<T extends DecoratorNode<any> = DecoratorNode<any>> {
  protected readonly injector = inject(Injector);
  protected readonly nodeKey = inject(NODE_KEY);
  protected readonly editorService = inject(TextEditorService);

  /**
   * Signal that holds the current node instance
   */
  private readonly node = signal<LexicalNode | null>(null);

  /**
   * Hook called when the node is updated
   * Fetches the latest node instance from the editor and updates the node signal
   */
  nodeUpdated(): void {
    const editor = this.editorService.editor;
    if (!editor) {
      this.node.set(null);
      return;
    }

    const editorState = editor.getEditorState();
    let updatedNode: LexicalNode | null = null;
    editorState.read(() => {
      updatedNode = $getNodeByKey(this.nodeKey);
    });
    this.node.set(updatedNode);
  }

  /**
   * Get the current decorator node state from the editor
   * Returns the typed decorator node instance
   */
  protected readonly currentNode = computed(() => {
    const nodeValue = this.node();
    return nodeValue instanceof DecoratorNode ? (nodeValue as T) : null;
  });
}
