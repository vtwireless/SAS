import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {LoginComponent} from './login.component';

describe('LoginComponent', () => {
    let component: LoginComponent;
    let fixture: ComponentFixture<LoginComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [LoginComponent]
        }).compileComponents();
    }))

    beforeEach(()=>{
        fixture = TestBed.createComponent(LoginComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    })

    it('should create', () => {
        expect(component).toBeTruthy();
    })

    it('component initial state', () => {
        expect(component.loading).toBeFalsy();
        expect(component.submitted).toBeFalsy();
        expect(component.responseMessage).toEqual('');
    });

    it('submitted true after onSubmit()', () => {
        component.onSubmit();
        expect(component.submitted).toBeTruthy();
    });

})