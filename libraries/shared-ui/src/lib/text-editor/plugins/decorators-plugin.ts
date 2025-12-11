import {
  Injectable,
  inject,
  ViewContainerRef,
  ComponentRef,
  ApplicationRef,
  Injector,
  Type,
} from '@angular/core';
import { LexicalEditor, $getRoot, $isDecoratorNode, DecoratorNode, NodeKey } from 'lexical';
import { TextEditorPlugin } from './plugin';
import { NODE_KEY } from '../decorators/base-node-component';
import { BaseNodeComponent } from '../decorators/base-node-component';

/**
 * Plugin for rendering DecoratorNodes as Angular components
 */
@Injectable()
export class DecoratorsPlugin implements TextEditorPlugin {
  private readonly appRef = inject(ApplicationRef);
  private readonly injector = inject(Injector);
  private editor: LexicalEditor | null = null;
  private viewContainerRef: ViewContainerRef | null = null;
  private decoratorComponents = new Map<NodeKey, ComponentRef<BaseNodeComponent>>();
  private unregisterListener: (() => void) | null = null;

  register(
    editor: LexicalEditor,
    rootElement?: HTMLElement,
    viewContainerRef?: ViewContainerRef,
  ): () => void {
    this.editor = editor;
    this.viewContainerRef = viewContainerRef || null;

    // Register decorator listener to render decorators when they change
    this.unregisterListener = editor.registerDecoratorListener(
      (decorators: Record<NodeKey, Type<BaseNodeComponent>>) => {
        this.renderDecorators(editor, decorators);
      },
    );

    return () => {
      this.cleanup();
    };
  }

  private renderDecorators(
    editor: LexicalEditor,
    decorators: Record<NodeKey, Type<BaseNodeComponent>>,
  ): void {
    if (!this.viewContainerRef) return;

    const decoratorKeys = new Set<NodeKey>(Object.keys(decorators) as NodeKey[]);

    // Remove decorators that no longer exist
    for (const [key, componentRef] of this.decoratorComponents.entries()) {
      if (!decoratorKeys.has(key)) {
        componentRef.destroy();
        this.decoratorComponents.delete(key);
      }
    }

    // Create/update decorator components
    for (const key in decorators) {
      if (Object.prototype.hasOwnProperty.call(decorators, key)) {
        const clazz = decorators[key];
        this.renderDecoratorNode(key, clazz, editor);
      }
    }
  }

  private renderDecoratorNode(
    key: string,
    clazz: Type<BaseNodeComponent>,
    editor: LexicalEditor,
  ): void {
    if (!this.viewContainerRef) return;

    const existingComponent = this.decoratorComponents.get(key);

    // Get the DOM element for this decorator
    const editorElement = editor.getRootElement();
    if (!editorElement) return;

    const decoratorElement = editorElement.querySelector(
      `[data-lexical-key="${key}"]`,
    ) as HTMLElement;
    if (!decoratorElement) return;

    if (existingComponent) {
      // Update existing component by calling nodeUpdated hook
      if (existingComponent.instance.nodeUpdated) {
        existingComponent.instance.nodeUpdated();
      }
      existingComponent.changeDetectorRef.detectChanges();
    } else {
      // Create new component
      this.createDecoratorComponent(key, clazz, decoratorElement);
    }
  }

  private createDecoratorComponent(
    nodeKey: string,
    clazz: Type<BaseNodeComponent>,
    element: HTMLElement,
  ): void {
    if (!this.viewContainerRef || !this.editor) return;

    // Get the component type from the node's decorate() method
    // Our custom nodes override decorate() to return Type<BaseNodeComponent>
    if (!clazz) return;

    // Create injector with NODE_KEY provider
    // Other services (like attachment service via provideAttachmentService()) should be provided by the user at a higher level
    const injector = Injector.create({
      providers: [{ provide: NODE_KEY, useValue: nodeKey }],
      parent: this.injector,
    });

    // Create the component dynamically
    const componentRef = this.viewContainerRef.createComponent(clazz, { injector });

    // Initialize the node signal by calling nodeUpdated
    componentRef.instance.nodeUpdated();

    // Attach component to the decorator element
    element.appendChild(componentRef.location.nativeElement);
    componentRef.changeDetectorRef.detectChanges();
    this.decoratorComponents.set(nodeKey, componentRef);
  }

  private cleanup(): void {
    for (const componentRef of this.decoratorComponents.values()) {
      componentRef.destroy();
    }
    this.decoratorComponents.clear();

    if (this.unregisterListener) {
      this.unregisterListener();
      this.unregisterListener = null;
    }

    this.editor = null;
    this.viewContainerRef = null;
  }
}
