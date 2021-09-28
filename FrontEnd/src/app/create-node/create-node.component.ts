import { Component } from '@angular/core';
import { Node, User } from '../_models/models';
import { Router } from '@angular/router';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
	selector: 'app-create-node',
	templateUrl: './create-node.component.html',
	styleUrls: ['./create-node.component.css'],
})
export class CreateNodeComponent {
	constructor(
		private httpRequests: HttpRequestsService,
		private router: Router
	) {
		if (localStorage.getItem('currentUser')) {
			let user = new User('', '', '');
			user = JSON.parse(localStorage.getItem('currentUser'));
			if (user.userType != 'ADMIN' && user.userType != 'SU') {
				this.router.navigate(['/']);
			} else {
				this.creatorID = user.id;
			}
		}
	}

	creatorID = '';
	trustLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
	nodeTypes = [
		'VT-CRTS-Node',
		'VT-Wireless-Registered Radar',
		'Mobile-Device',
	];
	statuses = ['ACTIVE', 'INACTIVE', 'OFFLINE', 'ONLINE', 'DAMAGED', 'OTHER'];

	model = new Node(
		null,
		'',
		'',
		0,
		'',
		null,
		null,
		null,
		null,
		'',
		false,
		'',
		''
	);

	submitted = false;

	onSubmit() {
		this.submitted = true;
		console.log(this.model);
		const user = JSON.parse(localStorage.getItem('currentUser'));
		this.httpRequests.createNode(this.model).subscribe(
			(data) => {
				if (data['status'] == '1') {
					this.router.navigate(['/node-list']);
				}
			},
			(error) => console.error(error)
		);
	}

	// TODO: Remove this when we're done
	get diagnostic() {
		return JSON.stringify(this.model);
	}

	newEvaluation() {
		this.model = new Node(
			null,
			'',
			'',
			0,
			'',
			null,
			null,
			null,
			null,
			'',
			false,
			'',
			''
		);
		//this.scale = 0;
	}

	//////// NOT SHOWN IN DOCS ////////

	showFormControls(form: any) {
		return (
			form &&
			form.controls['firstName'] &&
			form.controls['firstName'].value
		);
	}

	/////////////////////////////
	//evaluationForm = new FormGroup({
	// scale: new FormControl(''),
	//  tone: new FormControl(''),
	//  musicianship: new FormControl(''),
	//  technique: new FormControl(''),
	//  sightreading: new FormControl(''),
	// })
	public updateFrequencies() {
		if (this.model.maxFrequency < this.model.minFrequency) {
			this.model.maxFrequency = this.model.minFrequency;
		}
	}
	public updateSampleRate() {
		if (this.model.maxSampleRate < this.model.minSampleRate) {
			this.model.maxSampleRate = this.model.minSampleRate;
		}
	}
}
