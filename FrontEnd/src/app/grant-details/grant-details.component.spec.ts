import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GrantDetailsComponent } from './grant-details.component';

describe('GrantDetailsComponent', () => {
  let component: GrantDetailsComponent;
  let fixture: ComponentFixture<GrantDetailsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GrantDetailsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GrantDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
