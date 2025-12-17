import { Injectable, inject, computed, signal } from '@angular/core';
import { OrganizationService } from '../../application/services/organization.service';

@Injectable({
  providedIn: 'root',
})
export class OnboardingService {
  private readonly organizationService = inject(OrganizationService);

  // Check if user needs onboarding (no organizations)
  readonly needsOnboarding = computed(() => {
    const orgs = this.organizationService.organizationsList();
    return orgs.length === 0 && !this.organizationService.isLoading();
  });

  // Track if onboarding has been completed
  private readonly onboardingCompleted = signal<boolean>(
    localStorage.getItem('onboarding_completed') === 'true',
  );

  readonly isOnboardingCompleted = this.onboardingCompleted.asReadonly();

  /**
   * Check if user needs onboarding
   */
  shouldShowOnboarding(): boolean {
    // If already completed, don't show again
    if (this.onboardingCompleted()) {
      return false;
    }
    // Show if no organizations exist
    return this.needsOnboarding();
  }

  /**
   * Mark onboarding as completed
   */
  completeOnboarding(): void {
    this.onboardingCompleted.set(true);
    localStorage.setItem('onboarding_completed', 'true');
  }

  /**
   * Reset onboarding (for testing or if user wants to see it again)
   */
  resetOnboarding(): void {
    this.onboardingCompleted.set(false);
    localStorage.removeItem('onboarding_completed');
  }
}
