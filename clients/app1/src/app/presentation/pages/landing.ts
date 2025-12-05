import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { HeroSection } from '../components/hero-section';
import { FeaturesSection } from '../components/features-section';
import { Button } from 'shared-ui';

@Component({
  selector: 'app-landing',
  imports: [HeroSection, FeaturesSection, Button, RouterLink],
  template: `
    <div class="landing">
      <app-hero-section />
      <app-features-section />
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .landing {
        @apply min-h-screen;
        @apply flex flex-col;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Landing {}
