import { Component, Inject } from '@angular/core';
import {
	PrimaryUser,
	SecondaryUser,
	User,
	AppConstants,
} from '../_models/models';
import { Router } from '@angular/router';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
	selector: 'app-contact',
	templateUrl: './contact.component.html',
})
export class ContactComponent {
	PrimaryUsers: Array<PrimaryUser> = [];
	SecondaryUsers: Array<SecondaryUser> = [];
	GETAPI = AppConstants.GETURL;

	constructor(
		private httpRequests: HttpRequestsService,
		@Inject('BASE_URL') baseUrl: string,
		router: Router
	) {
		if (localStorage.getItem('currentUser')) {
			let user = new User('', '', '');
			user = JSON.parse(localStorage.getItem('currentUser'));
			if (user.userType != 'ADMIN') {
				router.navigate(['/']);
			}
		}

		this.httpRequests.getPrimaryUsers().subscribe(
			(data) => {
				if (data['status'] == '1') {
					this.PrimaryUsers = Object.assign([], data['primaryUsers']);
				}
			},
			(error) => console.error(error)
		);

		this.httpRequests.getSecondaryUsers().subscribe(
			(data) => {
				if (data['status'] == '1') {
					this.SecondaryUsers = Object.assign(
						[],
						data['secondaryUsers']
					);
				}
			},
			(error) => console.error(error)
		);
	}
}
