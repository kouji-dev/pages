import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { OnboardingService } from '../onboarding.service';
import { OrganizationService } from '../../../application/services/organization.service';

/**
 * Guard that redirects to onboarding if user needs onboarding
 * Use this on app routes to redirect users to onboarding first
 */
export const redirectOnboardingGuard: CanActivateFn = async (route, state) => {
  const onboardingService = inject(OnboardingService);
  const organizationService = inject(OrganizationService);
  const router = inject(Router);

  // Load organizations and wait for completion
  await organizationService.loadOrganizations();

  // Check if onboarding should be shown
  const isCompleted = onboardingService.isOnboardingCompleted();
  const orgs = organizationService.organizationsList();

  // If onboarding is not completed and user needs onboarding, redirect
  if (!isCompleted && orgs.length === 0) {
    router.navigate(['/onboarding']);
    return false;
  }

  // Allow access to the route
  return true;
};
