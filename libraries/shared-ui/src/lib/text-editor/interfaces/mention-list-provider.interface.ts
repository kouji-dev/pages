import { InjectionToken, Type, inject, type Provider } from '@angular/core';

/**
 * Interface for providing mention suggestions when user types "@"
 */
export interface TextEditorMentionListProviderInterface {
  /**
   * Search for mention suggestions based on query
   * @param query The search query (text after "@")
   * @returns Promise resolving to list of mention options
   */
  searchMentions(query: string): Promise<MentionOption[]>;
}

/**
 * A mention option that can be selected
 */
export interface MentionOption {
  /** Unique identifier for the mention (will be stored in content) */
  id: string;
  /** Display label for the mention */
  label: string;
  /** Optional avatar URL */
  avatarUrl?: string;
}

/**
 * Injection token for the mention list provider
 * @internal - Use provideMentionListProvider() and injectMentionListProvider() instead
 */
const MENTION_LIST_PROVIDER_TOKEN = new InjectionToken<TextEditorMentionListProviderInterface>(
  'MENTION_LIST_PROVIDER',
);

/**
 * Provides the mention list provider for the text editor
 * @param provider The mention list provider implementation
 * @returns Provider for the mention list provider
 */
export function provideMentionListProvider(
  provider: Type<TextEditorMentionListProviderInterface>,
): Provider {
  return {
    provide: MENTION_LIST_PROVIDER_TOKEN,
    useClass: provider,
  };
}

/**
 * Injects the mention list provider
 * @returns The mention list provider (throws if not provided)
 */
export function injectMentionListProvider(): TextEditorMentionListProviderInterface {
  return inject(MENTION_LIST_PROVIDER_TOKEN);
}
