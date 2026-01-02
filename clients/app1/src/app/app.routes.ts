import { Routes } from '@angular/router';
import { Demo } from './presentation/pages/demo';
import { Landing } from './presentation/pages/landing';
import { FeaturesPage } from './presentation/pages/features-page';
import { PricingPage } from './presentation/pages/pricing-page';
import { DashboardPage } from './features/dashboard/pages/dashboard/dashboard-page';
import { OrganizationsPage } from './features/organizations/pages/organizations/organizations-page.component';
import { OrganizationSettingsPage } from './features/organizations/pages/settings/organization-settings-page.component';
import { InvitationAcceptancePage } from './features/organizations/pages/invitation/invitation-acceptance-page.component';
import { ProfilePage } from './features/user/pages/profile/profile-page.component';
import { ProjectsPage } from './features/projects/pages/projects/projects-page';

import { IssueDetailPage } from './features/projects/pages/issue-detail/issue-detail-page';
import { SpacesPage } from './features/spaces/pages/spaces/spaces-page';
import { SpaceDetailPage } from './features/spaces/pages/detail/space-detail-page';
import { SpaceSettingsPage } from './features/spaces/pages/settings/space-settings-page';
import { PageDetailPage } from './features/pages/pages/detail/page-detail-page';
import { LoginPage } from './features/auth/pages/login/login-page.component';
import { RegisterPage } from './features/auth/pages/register/register-page.component';
import { ForgotPasswordPage } from './features/auth/pages/forgot-password/forgot-password-page.component';
import { ResetPasswordPage } from './features/auth/pages/reset-password/reset-password-page.component';
import { NotFoundComponent } from './presentation/pages/not-found.component';
import { AuthenticatedLayout } from './presentation/layout/authenticated-layout';
import { OrganizationLayout } from './presentation/layout/organization-layout';
import { authGuard } from './core/auth/guards/auth.guard';
import { loginGuard } from './core/auth/guards/login.guard';
import { OnboardingPage } from './core/onboarding/pages/onboarding-page/onboarding-page';
import { onboardingGuard } from './core/onboarding/guards/onboarding.guard';
import { redirectOnboardingGuard } from './core/onboarding/guards/redirect-onboarding.guard';
import { redirectToOrganizationGuard } from './core/organization/guards/redirect-to-organization.guard';
import { organizationExistsGuard } from './core/organization/guards/organization-exists.guard';
import { redirectOrganizationsGuard } from './core/organization/guards/redirect-organizations.guard';

export const routes: Routes = [
  {
    path: '',
    component: Landing,
    title: 'Pages - Build Better Together',
  },
  {
    path: 'demo',
    component: Demo,
    title: 'Component Demo - Pages',
  },
  {
    path: 'features',
    component: FeaturesPage,
    title: 'Features - Pages',
  },
  {
    path: 'pricing',
    component: PricingPage,
    title: 'Pricing - Pages',
  },
  {
    path: 'invitations/:token',
    component: InvitationAcceptancePage,
    title: 'Accept Invitation - Pages',
  },
  // Public authentication routes
  {
    path: 'login',
    component: LoginPage,
    canActivate: [loginGuard],
    title: 'Login - Pages',
  },
  {
    path: 'register',
    component: RegisterPage,
    title: 'Sign Up - Pages',
  },
  {
    path: 'forgot-password',
    component: ForgotPasswordPage,
    title: 'Forgot Password - Pages',
  },
  {
    path: 'reset-password',
    component: ResetPasswordPage,
    title: 'Reset Password - Pages',
  },
  // Onboarding route (requires authentication, but before app routes)
  {
    path: 'onboarding',
    component: OnboardingPage,
    canActivate: [authGuard, onboardingGuard],
    title: 'Onboarding - Pages',
  },
  // Protected routes (require authentication)
  {
    path: 'app',
    component: AuthenticatedLayout,
    canActivate: [authGuard, redirectOnboardingGuard],
    children: [
      {
        path: '',
        canActivate: [redirectToOrganizationGuard],
        redirectTo: '',
        pathMatch: 'full',
      },
      {
        path: 'organizations',
        component: OrganizationsPage,
        canActivate: [redirectOrganizationsGuard],
        title: 'Organizations - Pages',
      },
      {
        path: 'organizations/settings',
        component: OrganizationSettingsPage,
        title: 'Organization Settings - Pages',
      },
      {
        path: 'organizations/:organizationId',
        component: OrganizationLayout,
        canActivate: [organizationExistsGuard],
        children: [
          {
            path: '',
            redirectTo: 'projects',
            pathMatch: 'full',
          },
          {
            path: 'dashboard',
            component: DashboardPage,
            title: 'Dashboard - Pages',
          },
          {
            path: 'projects',
            children: [
              {
                path: '',
                component: ProjectsPage,
                title: 'Projects - Pages',
              },
              {
                path: ':projectId',
                children: [
                  {
                    path: '',
                    loadComponent: () =>
                      import('./features/projects/pages/detail/project-detail-page').then(
                        (m) => m.ProjectDetailPage,
                      ),
                    title: 'Project Board - Pages',
                  },
                  {
                    path: 'settings',
                    loadComponent: () =>
                      import('./features/projects/pages/settings/project-settings-page').then(
                        (m) => m.ProjectSettingsPage,
                      ),
                    title: 'Project Settings - Pages',
                  },
                  {
                    path: 'issues/:issueId',
                    component: IssueDetailPage,
                    title: 'Issue Details - Pages',
                  },
                ],
              },
            ],
          },
          {
            path: 'spaces',
            children: [
              {
                path: '',
                component: SpacesPage,
                title: 'Spaces - Pages',
              },
              {
                path: ':spaceId',
                component: SpaceDetailPage,
                title: 'Space Details - Pages',
                children: [
                  {
                    path: 'pages/:pageId',
                    component: PageDetailPage,
                    title: 'Page Details - Pages',
                  },
                  {
                    path: 'settings',
                    component: SpaceSettingsPage,
                    title: 'Space Settings - Pages',
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        path: 'profile',
        component: ProfilePage,
        title: 'Profile - Pages',
      },
    ],
  },
  // 404 - must be last
  {
    path: '**',
    component: NotFoundComponent,
    title: 'Page Not Found - Pages',
  },
];
