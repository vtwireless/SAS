import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SUDetailsComponent } from './SU-details.component';

describe('DetailsComponent', () => {
  let component: SUDetailsComponent;
  let fixture: ComponentFixture<SUDetailsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SUDetailsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SUDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
