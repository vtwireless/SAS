import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { User } from '../_models/models';
import { AuthenticationService } from '../_services/authentication.service';

@Component({
	selector: 'admin-login',
	styleUrls: ['./admin-login.component.css'],
	templateUrl: 'admin-login.component.html',
})
export class AdminLoginComponent implements OnInit, OnDestroy {
	loading = false;
	submitted = false;
	responseMessage = '';
	model = new LoginCreds('', '');

	constructor(
		private authenticationService: AuthenticationService,
		private router: Router
	) {
		if (localStorage.getItem('currentUser')) {
			this.router.navigate(['/']);
		}
	}

	ngOnInit() {
		document.getElementsByTagName('body')[0].classList.add('vt-loading-screen')
	}

	ngOnDestroy() {
		document.getElementsByTagName('body')[0].classList.remove('vt-loading-screen')
	}

	onSubmit() {
		this.submitted = true;
		this.loading = true;
		this.authenticationService.adminLogin(this.model).subscribe(
			(data) => {
				if (data['status'] == '1') {
					console.log(data);
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
