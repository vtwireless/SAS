import { Component, Injectable, OnDestroy, OnInit } from '@angular/core';
import { SecondaryUser } from '../_models/models';
import { Router } from '@angular/router';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
	selector: 'app-user-form',
	templateUrl: './create-su.component.html',
	styleUrls: ['./create-su.component.css'],
})
@Injectable()
export class CreateSUComponent implements OnInit, OnDestroy{
	constructor(
		private httpRequests: HttpRequestsService,
		private router: Router
	) {}

	ngOnInit() {
		document.getElementsByTagName('body')[0].classList.add('vt-loading-screen')
	}

	ngOnDestroy() {
		document.getElementsByTagName('body')[0].classList.remove('vt-loading-screen')
	}

	model = new SecondaryUser('', '', '', '', '', '', '', '0,0', '');
	submitted = false;
	message = '';
	uniqueEmail = true;

	onSubmit() {
		console.log('hu');
		this.submitted = true;
		this.httpRequests.createSecondaryAccount(this.model).subscribe(
			(data) => {
				console.log(data);
				if (data['status'] == '1') {
					console.log('good');
					this.message =
						'You have successfully created an account with the VT SAS!';
					localStorage.setItem('registered', 'true');

					setTimeout(() => {
						this.router.navigate(['/login']);
					}, 2000);
				} else {
					if (data['exists'] == '1') {
						this.message = 'Email Already In Use';
					}
				}
			},
			(error) => console.error(error)
		);
	}

	checkEmailAvail() {
		this.httpRequests.checkEmail(this.model).subscribe(
			(data) => {
				if (data['exists'] == '1') {
					this.message = 'Email Already in Use.';
					this.uniqueEmail = false;
				} else {
					this.message = '';
					this.uniqueEmail = true;
				}
			},
			(error) => console.error(error)
		);
	}

	newSU() {
		this.model = new SecondaryUser('', '', '', '', '', '', '', '0,0', '');
		console.log('New SU ');
	}

	showFormControls(form: any) {
		return (
			form &&
			form.controls['firstName'] &&
			form.controls['firstName'].value
		);
	}
}
