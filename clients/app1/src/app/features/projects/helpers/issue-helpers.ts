import { IconName } from 'shared-ui';

export type IssueType = 'task' | 'bug' | 'story' | 'epic';
export type IssuePriority = 'low' | 'medium' | 'high' | 'critical';

export interface IssueTypeConfig {
  icon: IconName;
  label: string;
  bgColor: string;
  textColor: string;
}

export interface IssuePriorityConfig {
  icon: IconName;
  label: string;
  bgColor: string;
  textColor: string;
  iconColor: string;
}

/**
 * Issue type configuration with icons and colors
 */
export const ISSUE_TYPE_CONFIG: Record<IssueType, IssueTypeConfig> = {
  task: {
    icon: 'list',
    label: 'Task',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
  },
  bug: {
    icon: 'bug',
    label: 'Bug',
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
  },
  story: {
    icon: 'book-open',
    label: 'Story',
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
  },
  epic: {
    icon: 'layers',
    label: 'Epic',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-800',
  },
};

/**
 * Issue priority configuration with icons and colors
 */
export const ISSUE_PRIORITY_CONFIG: Record<IssuePriority, IssuePriorityConfig> = {
  low: {
    icon: 'arrow-down',
    label: 'Low',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    iconColor: 'text-gray-600',
  },
  medium: {
    icon: 'minus',
    label: 'Medium',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    iconColor: 'text-blue-600',
  },
  high: {
    icon: 'arrow-up',
    label: 'High',
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-800',
    iconColor: 'text-orange-600',
  },
  critical: {
    icon: 'zap',
    label: 'Critical',
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    iconColor: 'text-red-600',
  },
};

/**
 * Get issue type configuration
 */
export function getIssueTypeConfig(type: IssueType): IssueTypeConfig {
  return ISSUE_TYPE_CONFIG[type] || ISSUE_TYPE_CONFIG.task;
}

/**
 * Get issue priority configuration
 */
export function getIssuePriorityConfig(priority: IssuePriority): IssuePriorityConfig {
  return ISSUE_PRIORITY_CONFIG[priority] || ISSUE_PRIORITY_CONFIG.medium;
}
