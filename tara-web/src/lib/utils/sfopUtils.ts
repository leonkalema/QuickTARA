import type { DamageScenario } from '../types/damageScenario';

export interface SfopRating {
  safety: string;
  financial: string;
  operational: string;
  privacy: string;
}

export function getOverallSfopRating(scenario: DamageScenario): string {
  // Backend stores SFOP data in impact_rating object
  const impacts = [
    scenario.impact_rating?.safety,
    scenario.impact_rating?.financial,
    scenario.impact_rating?.operational,
    scenario.impact_rating?.privacy
  ].filter(impact => impact && impact !== 'negligible');

  if (impacts.length === 0) return 'negligible';

  const severityOrder = ['negligible', 'moderate', 'major', 'severe'];
  let maxSeverity = 0;
  
  impacts.forEach(impact => {
    const index = severityOrder.indexOf(impact || 'negligible');
    if (index > maxSeverity) {
      maxSeverity = index;
    }
  });

  return severityOrder[maxSeverity];
}

export function getSfopBadgeClass(_impact: string): string {
  return '';
}

export function getSfopBadgeStyle(impact: string): string {
  switch (impact) {
    case 'severe': return 'background: var(--color-risk-high-bg); color: var(--color-risk-high);';
    case 'major': return 'background: var(--color-risk-medium-bg); color: var(--color-risk-medium);';
    case 'moderate': return 'background: var(--color-risk-low-bg); color: var(--color-risk-low);';
    case 'negligible': return 'background: color-mix(in srgb, var(--color-status-accepted-text, #10b981) 15%, transparent); color: var(--color-status-accepted-text, #10b981);';
    default: return 'background: var(--color-bg-elevated); color: var(--color-text-tertiary);';
  }
}

export function getCIABadgeClass(_isActive: boolean): string {
  return '';
}

export function getCIABadgeStyle(isActive: boolean): string {
  return isActive
    ? 'background: var(--color-risk-high-bg); color: var(--color-risk-high); border: 1px solid color-mix(in srgb, var(--color-risk-high) 30%, transparent);'
    : 'background: var(--color-bg-elevated); color: var(--color-text-tertiary); border: 1px solid var(--color-border-subtle);';
}

export function getSfopImpacts(scenario: DamageScenario): SfopRating {
  return {
    safety: scenario.impact_rating?.safety || 'negligible',
    financial: scenario.impact_rating?.financial || 'negligible',
    operational: scenario.impact_rating?.operational || 'negligible',
    privacy: scenario.impact_rating?.privacy || 'negligible'
  };
}
