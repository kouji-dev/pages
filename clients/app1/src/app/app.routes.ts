import { Routes } from '@angular/router';
import { Demo } from './presentation/pages/demo';
import { Landing } from './presentation/pages/landing';
import { FeaturesPage } from './presentation/pages/features-page';
import { PricingPage } from './presentation/pages/pricing-page';
import { OrganizationsPage } from './presentation/pages/organizations-page';
import { OrganizationSettingsPage } from './presentation/pages/organization-settings-page';
import { InvitationAcceptancePage } from './presentation/pages/invitation-acceptance-page';
import { ProfilePage } from './presentation/pages/profile-page';
import { LoginPage } from './presentation/pages/login-page.component';
import { RegisterPage } from './presentation/pages/register-page.component';
import { NotFoundComponent } from './presentation/pages/not-found.component';
import { AuthenticatedLayout } from './presentation/layout/authenticated-layout';
import { authGuard } from './application/guards/auth.guard';

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
    title: 'Login - Pages',
  },
  {
    path: 'register',
    component: RegisterPage,
    title: 'Sign Up - Pages',
  },
  // Protected routes (require authentication)
  {
    path: 'app',
    component: AuthenticatedLayout,
    canActivate: [authGuard],
    children: [
      {
        path: 'organizations',
        component: OrganizationsPage,
        title: 'Organizations - Pages',
      },
      {
        path: 'organizations/:id/settings',
        component: OrganizationSettingsPage,
        title: 'Organization Settings - Pages',
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
