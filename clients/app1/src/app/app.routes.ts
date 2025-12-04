import { Routes } from '@angular/router';
import { Demo } from './presentation/pages/demo';

export const routes: Routes = [
  {
    path: 'demo',
    component: Demo,
    title: 'Component Demo - Pages',
  },
  {
    path: '',
    redirectTo: '/demo',
    pathMatch: 'full',
  },
];
