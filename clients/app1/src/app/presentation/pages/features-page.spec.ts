import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FeaturesPage } from './features-page';
import { Button, Icon } from 'shared-ui';

describe('FeaturesPage', () => {
  let component: FeaturesPage;
  let fixture: ComponentFixture<FeaturesPage>;
  let element: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FeaturesPage, Button, Icon],
    }).compileComponents();

    fixture = TestBed.createComponent(FeaturesPage);
    component = fixture.componentInstance;
    element = fixture.nativeElement;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render page title', () => {
    const title = element.querySelector('.features-page_title');
    expect(title).toBeTruthy();
    expect(title?.textContent).toContain('Everything You Need to Build Better Together');
  });

  it('should render feature categories', () => {
    const categories = element.querySelectorAll('.features-page_category');
    expect(categories.length).toBeGreaterThan(0);
  });

  it('should render CTA buttons in header', () => {
    const buttons = element.querySelectorAll('.features-page_header-actions lib-button');
    expect(buttons.length).toBe(2);
  });

  it('should render feature cards for each category', () => {
    const featureCards = element.querySelectorAll('.features-page_feature-card');
    expect(featureCards.length).toBeGreaterThan(0);
  });

  it('should render CTA section at the bottom', () => {
    const ctaSection = element.querySelector('.features-page_cta');
    expect(ctaSection).toBeTruthy();
  });
});
