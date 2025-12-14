import { Injectable, inject } from '@angular/core';
import type { TextEditorMentionListProviderInterface, MentionOption } from 'shared-ui';
import { ProjectMembersService } from './project-members.service';

/**
 * Implementation of TextEditorMentionListProviderInterface for the text editor
 * Uses ProjectMembersService to search for mention suggestions via API
 */
@Injectable({
  providedIn: 'root',
})
export class TextEditorMentionService implements TextEditorMentionListProviderInterface {
  private readonly projectMembersService = inject(ProjectMembersService);

  async searchMentions(query: string): Promise<MentionOption[]> {
    const trimmedQuery = query.trim();

    try {
      // Call API to search members
      // If query is empty, API will return all members (search parameter is optional)
      // ProjectMembersService will use current project from navigation service
      const members = await this.projectMembersService.searchProjectMembers(
        undefined, // Use current project from navigation
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
