import { Routes } from '@angular/router';
import { Demo } from './presentation/pages/demo';
import { Landing } from './presentation/pages/landing';
import { FeaturesPage } from './presentation/pages/features-page';
import { PricingPage } from './presentation/pages/pricing-page';

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
];
