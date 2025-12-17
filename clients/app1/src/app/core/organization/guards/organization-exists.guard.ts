import { inject } from '@angular/core';
import { Router, CanActivateFn, ActivatedRouteSnapshot } from '@angular/router';
import { OrganizationService } from '../../../application/services/organization.service';

/**
 * Guard that ensures the organization in the route exists
 * Redirects to /app/organizations if organization doesn't exist
 */
export const organizationExistsGuard: CanActivateFn = async (route: ActivatedRouteSnapshot) => {
  const organizationService = inject(OrganizationService);
  const router = inject(Router);

  const organizationId = route.paramMap.get('organizationId');
  if (!organizationId) {
    router.navigate(['/app/organizations']);
    return false;
  }

  // Load organizations and wait for completion
  await organizationService.loadOrganizations();

  const organizations = organizationService.organizationsList();
  const orgExists = organizations.some((org) => org.id === organizationId);

  if (!orgExists) {
    // Organization doesn't exist, redirect to organizations page
    router.navigate(['/app/organizations']);
    return false;
  }

  return true;
};
