import iconNodes from 'lucide-static/icon-nodes.json';

// Extract icon names as a union type directly from iconNodes keys
// icon-nodes.json already uses kebab-case keys
export type IconName = keyof typeof iconNodes;

// Get all icon names as an array (sorted) for runtime use
export const lucideIconNames: IconName[] = (Object.keys(iconNodes) as IconName[])
  .sort((a, b) => a.localeCompare(b));

// IconNodes type derived from lucideIconNames (list of strings)
export type IconNodes = IconName[];