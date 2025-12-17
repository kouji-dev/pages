import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { OnboardingService } from '../onboarding.service';
import { OrganizationService } from '../../../application/services/organization.service';

export const onboardingGuard: CanActivateFn = async (route, state) => {
  const onboardingService = inject(OnboardingService);
  const organizationService = inject(OrganizationService);
  const router = inject(Router);

  // Load organizations and wait for completion
  await organizationService.loadOrganizations();

  // Check if onboarding is completed
  if (onboardingService.isOnboardingCompleted()) {
    router.navigate(['/app']);
    return false;
  }

  // Check if organizations exist
  const orgs = organizationService.organizationsList();
  if (orgs.length > 0) {
    onboardingService.completeOnboarding();
    router.navigate(['/app']);
    return false;
  }

  // Allow access to onboarding page
  return true;
};
