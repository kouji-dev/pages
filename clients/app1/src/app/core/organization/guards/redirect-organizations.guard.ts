import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { OrganizationService } from '../../../application/services/organization.service';
import { OnboardingService } from '../../onboarding/onboarding.service';

/**
 * Guard that redirects /app/organizations to the first organization's dashboard
 * If no organizations exist and onboarding is not completed, redirects to onboarding
 * If no organizations exist but onboarding is completed, allows access (edge case)
 */
export const redirectOrganizationsGuard: CanActivateFn = async (route, state) => {
  const organizationService = inject(OrganizationService);
  const onboardingService = inject(OnboardingService);
  const router = inject(Router);

  // Load organizations and wait for completion
  await organizationService.loadOrganizations();

  const organizations = organizationService.organizationsList();

  if (organizations.length > 0) {
    // Organizations exist, redirect to first organization's dashboard
    const firstOrg = organizations[0];
    router.navigate(['/app/organizations', firstOrg.id, 'dashboard']);
    return false;
  }

  // No organizations - check if onboarding is needed
  if (!onboardingService.isOnboardingCompleted()) {
    // Redirect to onboarding to create first organization
    router.navigate(['/onboarding']);
    return false;
  }

  // Edge case: onboarding completed but no organizations (shouldn't happen normally)
  // Allow access to organizations page so user can create one
  return true;
};
