import { Component, ChangeDetectionStrategy } from '@angular/core';
import { HeroSection } from '../components/hero-section';
import { FeaturesSection } from '../components/features-section';
import { PublicNav } from '../components/public-nav';
import { Footer } from '../components/footer';

@Component({
  selector: 'app-landing',
  imports: [PublicNav, HeroSection, FeaturesSection, Footer],
  template: `
    <div class="landing">
      <app-public-nav />
      <main class="landing_main">
        <app-hero-section />
        <app-features-section />
      </main>
      <app-footer />
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .landing {
        @apply min-h-screen;
        @apply flex flex-col;
      }

      .landing_main {
        @apply flex-1;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Landing {}
