import { InjectionToken } from '@angular/core';
import { TextEditorPlugin } from './plugins/plugin';

/**
 * Injection token for providing TextEditor plugins.
 * Use multi: true providers to register additional plugins.
 */
export const TEXT_EDITOR_PLUGINS = new InjectionToken<TextEditorPlugin[]>('TEXT_EDITOR_PLUGINS');
