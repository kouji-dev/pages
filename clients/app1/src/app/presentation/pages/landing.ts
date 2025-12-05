import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { HeroSection } from '../components/hero-section';
import { Button } from 'shared-ui';

@Component({
  selector: 'app-landing',
  imports: [HeroSection, Button, RouterLink],
  template: `
    <div class="landing">
      <app-hero-section />
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
