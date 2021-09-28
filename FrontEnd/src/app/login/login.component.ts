import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AppConstants, User } from '../_models/models';
import { AuthenticationService } from '../_services/authentication.service';
import { first } from 'rxjs/operators';

@Component({
	selector: 'login',
	styleUrls: ['./login.component.css'],
	templateUrl: 'login.component.html',
})
export class LoginComponent implements OnInit, OnDestroy {
	loading = false;
	submitted = false;
	responseMessage = '';
	model = new LoginCreds('', '');
	POSTAPI = AppConstants.POSTURL;
	successfullyRegistered = false;

	constructor(
		private router: Router,
		private authenticationService: AuthenticationService
	) {
		if (localStorage.getItem('currentUser')) {
			console.log(localStorage.getItem('currentUser'));
			this.router.navigate(['/']);
		}
		if (localStorage.getItem('registered') == 'true') {
			localStorage.removeItem('registered');
			this.successfullyRegistered = true;
		}
	}

	ngOnInit() {
		document.getElementsByTagName('body')[0].classList.add('vt-loading-screen')
	}

	ngOnDestroy() {
		document.getElementsByTagName('body')[0].classList.remove('vt-loading-screen')
	}

	onSubmit() {
		console.log("Submitting");
		this.submitted = true;
		this.loading = true;
		this.authenticationService.suLogin(this.model)   // .pipe(first())
			.subscribe(data => {
				console.log(data);
				if (data['status'] == '1') {
					const user = new User(
						data['id'],
						data['userType'],
						data['name']
					);
					localStorage.setItem('currentUser', JSON.stringify(user));
					this.responseMessage = '';
					window.location.reload();
				} else {
					this.responseMessage = 'Incorrect Username or Password';
				}
			},
			(error) => {
				console.error(error)
				this.responseMessage = 'Sorry, there was an error logging in, please try again later';

			}
		);
	}
}

export class LoginCreds {
	constructor(public username: string, public password: string) {}
}
