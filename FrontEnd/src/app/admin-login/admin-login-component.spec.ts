import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {AdminLoginComponent} from './admin-login.component';
import {validAdminUser,blankUser} from '../../mocks';

describe('AdminLoginComponent', () => {
    let component: AdminLoginComponent;
    let fixture: ComponentFixture<AdminLoginComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [AdminLoginComponent]
        }).compileComponents();
    }))

    beforeEach(()=>{
        fixture = TestBed.createComponent(AdminLoginComponent);
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