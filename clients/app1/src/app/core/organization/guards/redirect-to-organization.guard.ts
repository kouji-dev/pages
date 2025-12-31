import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { OrganizationService } from '../../../application/services/organization.service';

/**
 * Guard that redirects /app to the first organization's dashboard
 * If no organizations exist, redirects to /onboarding
 */
export const redirectToOrganizationGuard: CanActivateFn = async (route, state) => {
  const organizationService = inject(OrganizationService);
  const router = inject(Router);

  // Load organizations and wait for completion
  await organizationService.loadOrganizations();

  const organizations = organizationService.organizationsList();

  if (organizations.length === 0) {
    // No organizations, redirect to onboarding page
    router.navigate(['/onboarding']);
    return false;
  }

  // Redirect to first organization's dashboard
  const firstOrg = organizations[0];
  router.navigate(['/app/organizations', firstOrg.id, 'dashboard']);
  return false;
};
