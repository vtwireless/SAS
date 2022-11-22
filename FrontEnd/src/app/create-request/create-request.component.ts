import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { FormGroup, FormControl } from '@angular/forms';
import { Evaluation } from '../_models/models';
import { ActivatedRoute } from '@angular/router';
import {
	GrantRequest,
	User,
	SecondaryUser,
	AppConstants,
} from '../_models/models';
//import {MatSliderModule} from '@angular/material/slider';
import { Router } from '@angular/router';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
	selector: 'app-create-request',
	templateUrl: './create-request.component.html',
	styleUrls: ['./create-request.component.css'],
})
export class CreateRequestComponent {
	GETAPI = AppConstants.GETURL;
	POSTAPI = AppConstants.POSTURL;
	minDate = '2021-01-01-T00:00';
	locationValid = false;
	locationSet = false;
	isAdmin = false;
	isSU = false;
	SecondaryUsers: Array<SecondaryUser> = [];
	model = new GrantRequest();
	creatorID = '';
	trustLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
	dataTypes = ['AUDIO', 'IMAGE-VIDEO', 'DRONE', 'RADAR', 'RADIO', 'OTHER'];
	nodes: Array<Node> = []
	failResponseMessage = '';
	submitted = false;

	constructor(
		private route: ActivatedRoute,
		private httpRequests: HttpRequestsService,
		private router: Router
	) {}
	ngOnInit() {
		//console.log(this.datePipe.transform(this.now,"yyyy-MM-ddTHH:mm"));
		if (localStorage.getItem('currentUser')) {
			let user = new User('', '', '');
			user = JSON.parse(localStorage.getItem('currentUser'));
			if (user.userType == 'ADMIN') {
				this.isAdmin = true;
				this.httpRequests.getSecondaryUsers().subscribe(
					(data) => {
						if (data['status'] == 1) {
							this.SecondaryUsers = data['secondaryUsers'];
							this.model.secondaryUserID = user.id;
						}
					},
					(error) => console.error(error)
				);
			} else if (user.userType == 'SU') {
				this.creatorID = user.id;
				this.isSU = true;
			} else {
				this.router.navigate(['/']);
			}
		}

		// Fetch Nodes from DB
		this.httpRequests.getAllNodes().subscribe((data) => {
			if (data['status'] == '1') {
				for (const node of data['nodes']) {
					this.nodes.push(node.cbsdID)
				}
			}
		});

		this.model.maxVelocity = 0;
		this.model.frequencyAbsolute = false;
		this.model.mobility = false;
		this.model.minFrequency = 3550;
		this.model.maxFrequency = 3550;
		this.model.preferredFrequency = 3550;
		this.setStartTime();
	}



	onSubmit() {
		this.submitted = true;
		console.log("Grant Request:", JSON.stringify(this.model));
		this.model.minFrequency *= 1000000;
		this.model.maxFrequency *= 1000000;
		this.model.preferredFrequency *= 1000000;
		// this.model.minBandwidth *= 1000000;
		// this.model.maxBandwidth *= 1000000;
		// this.model.preferredBandwidth *= 1000000;
		console.log(this.model);
		this.httpRequests.createRequest(this.model, this.isAdmin).subscribe(
			(data) => {
				if (data['grantResponse'][0]['response']['responseMessage'] == 'SUCCESS') {
					this.router.navigate(['/grant-list']);
				}else{
					this.router.navigate(['/grant-message'])
					this.failResponseMessage = data['grantResponse'][0]['response']['responseMessage'];
				}
			},
			(error) => console.error(error)
		);
	}

	// TODO: Remove this when we're done
	get diagnostic() {
		return JSON.stringify(this.model);
	}

	newRequest() {
		this.model = new GrantRequest();
		this.model.minFrequency = 3550*1000000;
		this.model.maxVelocity = 0;
		this.model.maxFrequency = 3550*1000000;
		this.model.preferredFrequency = 3550*1000000;
		this.model.mobility = false;
		this.model.frequencyAbsolute = false;
		this.setStartTime();
		this.locationSet = false;
		this.locationValid = false;
	}

	showFormControls(form: any) {
		return (
			form &&
			form.controls['firstName'] &&
			form.controls['firstName'].value
		);
	}

	public updatePreferredBandwidth() {
		if (this.model.preferredBandwidth < this.model.minBandwidth) {
			this.model.preferredBandwidth = this.model.minBandwidth;
		}
	}

	public updateFrequencies() {
		if (this.model.maxFrequency < this.model.minFrequency) {
			this.model.maxFrequency = this.model.minFrequency;
		}
		if (this.model.preferredFrequency < this.model.minFrequency) {
			this.model.preferredFrequency = this.model.minFrequency;
		}
		if (this.model.preferredFrequency > this.model.maxFrequency) {
			this.model.maxFrequency = this.model.preferredFrequency;
		}
		/*if (this.model.preferredFrequency < this.model.minFrequency){
            this.model.preferredFrequency = this.model.minFrequency;
        }
        if (this.model.maxFrequency < this.model.preferredFrequency){
            this.model.preferredFrequency = this.model.maxFrequency;
        }*/
		this.frequencyBeAbsolute();
	}

	public updateTimes() {
		if (
			this.model.endTime < this.model.startTime ||
			this.model.endTime == null
		) {
			this.model.endTime = this.model.startTime;
		}
	}

	public frequencyBeAbsolute() {
		if (this.model.frequencyAbsolute == true) {
			this.model.minFrequency = Math.max(
				this.model.minFrequency,
				this.model.maxFrequency,
				this.model.preferredFrequency
			);
			this.model.maxFrequency = Math.max(
				this.model.minFrequency,
				this.model.maxFrequency,
				this.model.preferredFrequency
			);
			this.model.preferredFrequency = Math.max(
				this.model.minFrequency,
				this.model.maxFrequency,
				this.model.preferredFrequency
			);
		}
	}

	public setStartTime() {
		let now = new Date();
		var coeff = 1000 * 60 * 5;
		var rounded = new Date(Math.ceil(now.getTime() / coeff) * coeff);
		let MM = rounded.getMonth() + 1;
		let month = rounded.getMonth().toString();
		let dd = rounded.getDate();
		let date = rounded.getDate().toString();
		let HH = rounded.getHours();
		let hours = rounded.getHours().toString();
		let mm = rounded.getMinutes();
		let minutes = rounded.getMinutes().toString();

		if (MM < 10) {
			month = '0' + MM;
		}
		if (dd < 10) {
			date = '0' + dd;
		}
		if (HH < 10) {
			hours = '0' + HH;
		}
		if (mm < 10) {
			minutes = '0' + mm;
		}
		//console.log(rounded.getFullYear()+'-'+month+'-'+date+'T'+hours+':'+minutes);
		this.model.startTime =
			rounded.getFullYear() +
			'-' +
			month +
			'-' +
			date +
			'T' +
			hours +
			':' +
			minutes;
		this.minDate = this.model.startTime;
		//console.log(this.minDate);
	}

	public checkLocationValid() {
		this.locationSet = true;
		this.model.location = this.model.location.replace(' ', '');
		this.model.location = this.model.location.replace(
			/[abcdefghijklmnopqrstuvwxyz!@#$%^&*();:<>?]/gi,
			''
		);
		var split = this.model.location.split(',');
		if (split.length == 2) {
			if (
				Number(split[0]) <= 90 &&
				Number(split[0]) >= -90 &&
				Number(split[1]) <= 180 &&
				Number(split[1]) >= -180 &&
				split[0].length > 5 &&
				split[1].length > 5
			) {
				this.locationValid = true;
			} else {
				this.locationValid = false;
			}
		} else {
			this.locationValid = false;
		}
		//console.log(this.locationValid);
	}
}
