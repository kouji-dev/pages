import { Injectable, inject, computed } from '@angular/core';
import type { TextEditorMentionListProviderInterface, MentionOption } from 'shared-ui';
import { NavigationService } from './navigation.service';
import { ProjectMembersApiService } from './project-members-api.service';

/**
 * Implementation of TextEditorMentionListProviderInterface for the text editor
 * Uses ProjectMembersApiService to search for mention suggestions via API
 */
@Injectable({
  providedIn: 'root',
})
export class TextEditorMentionService implements TextEditorMentionListProviderInterface {
  private readonly projectMembersApi = inject(ProjectMembersApiService);
  private readonly navigationService = inject(NavigationService);

  // Get current project ID
  private readonly projectId = computed(() => {
    return this.navigationService.currentProjectId();
  });

  async searchMentions(query: string): Promise<MentionOption[]> {
    const projectId = this.projectId();
    if (!projectId) {
      // If no project context, return empty array
      return [];
    }

    const trimmedQuery = query.trim();

    // If query is empty, return empty array (don't load all members)
    // The user should type something to search
    if (!trimmedQuery) {
      return [];
    }

    try {
      // Call API to search members (backend needs to support 'search' parameter)
      const members = await this.projectMembersApi.searchProjectMembers(
        projectId,
        trimmedQuery,
        20, // Limit to 20 results for mentions
      );

      // Map to MentionOption format
      return members.map((member) => ({
        id: member.user_id,
        label: member.user_name,
        avatarUrl: member.avatar_url,
      }));
    } catch (error) {
      console.error('Failed to search project members for mentions:', error);
      // Return empty array on error to avoid breaking the UI
      return [];
    }
  }
}
