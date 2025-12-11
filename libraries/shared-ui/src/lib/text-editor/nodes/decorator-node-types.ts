import { type Type } from '@angular/core';
import { BaseNodeComponent } from '../decorators/base-node-component';

/**
 * Shared type for decorator node component types
 * All decorator nodes should return a component type that extends BaseNodeComponent
 */
export type DecoratorNodeComponentType<T extends BaseNodeComponent<any> = BaseNodeComponent<any>> =
  Type<T>;
