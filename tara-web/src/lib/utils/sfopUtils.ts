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

export function getSfopBadgeClass(impact: string): string {
  switch (impact) {
    case 'severe': return 'bg-red-100 text-red-800';
    case 'major': return 'bg-orange-100 text-orange-800';
    case 'moderate': return 'bg-yellow-100 text-yellow-800';
    case 'negligible': return 'bg-green-100 text-green-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

export function getCIABadgeClass(isActive: boolean): string {
  return isActive 
    ? 'bg-red-100 text-red-800 border border-red-200' 
    : 'bg-gray-100 text-gray-500 border border-gray-200';
}

export function getSfopImpacts(scenario: DamageScenario): SfopRating {
  return {
    safety: scenario.impact_rating?.safety || 'negligible',
    financial: scenario.impact_rating?.financial || 'negligible',
    operational: scenario.impact_rating?.operational || 'negligible',
    privacy: scenario.impact_rating?.privacy || 'negligible'
  };
}
