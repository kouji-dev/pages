import { Routes } from '@angular/router';
import { Demo } from './presentation/pages/demo';
import { Landing } from './presentation/pages/landing';
import { FeaturesPage } from './presentation/pages/features-page';
import { PricingPage } from './presentation/pages/pricing-page';
import { OrganizationsPage } from './presentation/pages/organizations-page';
import { OrganizationSettingsPage } from './presentation/pages/organization-settings-page';
import { InvitationAcceptancePage } from './presentation/pages/invitation-acceptance-page';
import { ProfilePage } from './presentation/pages/profile-page';
import { ProjectsPage } from './presentation/pages/projects-page';
import { ProjectDetailPage } from './presentation/pages/project-detail-page';
import { IssueDetailPage } from './presentation/pages/issue-detail-page';
import { SpacesPage } from './presentation/pages/spaces-page';
import { SpaceDetailPage } from './presentation/pages/space-detail-page';
import { SpaceSettingsPage } from './presentation/pages/space-settings-page';
import { PageDetailPage } from './presentation/pages/page-detail-page';
import { LoginPage } from './presentation/pages/login-page.component';
import { RegisterPage } from './presentation/pages/register-page.component';
import { ForgotPasswordPage } from './presentation/pages/forgot-password-page.component';
import { ResetPasswordPage } from './presentation/pages/reset-password-page.component';
import { NotFoundComponent } from './presentation/pages/not-found.component';
import { AuthenticatedLayout } from './presentation/layout/authenticated-layout';
import { OrganizationLayout } from './presentation/layout/organization-layout';
import { authGuard } from './application/guards/auth.guard';
import { loginGuard } from './application/guards/login.guard';

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
  // Protected routes (require authentication)
  {
    path: 'app',
    component: AuthenticatedLayout,
    canActivate: [authGuard],
    children: [
      {
        path: '',
        redirectTo: 'organizations',
        pathMatch: 'full',
      },
      {
        path: 'organizations',
        component: OrganizationsPage,
        title: 'Organizations - Pages',
      },
      {
        path: 'organizations/:organizationId',
        component: OrganizationLayout,
        children: [
          {
            path: '',
            redirectTo: 'projects',
            pathMatch: 'full',
          },
          {
            path: 'projects',
            component: ProjectsPage,
            title: 'Projects - Pages',
          },
          {
            path: 'spaces',
            component: SpacesPage,
            title: 'Spaces - Pages',
          },
        ],
      },
      {
        path: 'organizations/:organizationId/settings',
        component: OrganizationSettingsPage,
        title: 'Organization Settings - Pages',
      },
      {
        path: 'organizations/:organizationId/spaces/:spaceId',
        component: SpaceDetailPage,
        children: [
          {
            path: 'pages/:pageId',
            component: PageDetailPage,
            title: 'Page Details - Pages',
          },
        ],
      },
      {
        path: 'organizations/:organizationId/spaces/:spaceId/settings',
        component: SpaceSettingsPage,
        title: 'Space Settings - Pages',
      },
      {
        path: 'organizations/:organizationId/projects/:projectId',
        children: [
          {
            path: '',
            component: ProjectDetailPage,
            title: 'Project Details - Pages',
          },
          {
            path: 'issues/:issueId',
            component: IssueDetailPage,
            title: 'Issue Details - Pages',
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
