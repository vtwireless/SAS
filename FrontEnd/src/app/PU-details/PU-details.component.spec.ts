import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PUDetailsComponent } from './PU-details.component';

describe('PUDetailsComponent', () => {
  let component: PUDetailsComponent;
  let fixture: ComponentFixture<PUDetailsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PUDetailsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PUDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
