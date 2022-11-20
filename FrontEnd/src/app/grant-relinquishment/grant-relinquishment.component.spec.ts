import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GrantRelinquishmentComponent } from './grant-relinquishment.component';

describe('GrantRelinquishmentComponent', () => {
  let component: GrantRelinquishmentComponent;
  let fixture: ComponentFixture<GrantRelinquishmentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GrantRelinquishmentComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GrantRelinquishmentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
