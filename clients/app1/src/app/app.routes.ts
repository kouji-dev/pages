import { Routes } from '@angular/router';
import { Demo } from './presentation/pages/demo';
import { Landing } from './presentation/pages/landing';
import { FeaturesPage } from './presentation/pages/features-page';
import { PricingPage } from './presentation/pages/pricing-page';
import { OrganizationsPage } from './presentation/pages/organizations-page';
import { OrganizationSettingsPage } from './presentation/pages/organization-settings-page';
import { AuthenticatedLayout } from './presentation/layout/authenticated-layout';

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
    path: 'app',
    component: AuthenticatedLayout,
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
    ],
  },
];
