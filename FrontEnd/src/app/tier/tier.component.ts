import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { FormGroup, FormControl } from '@angular/forms';
import { Evaluation } from '../_models/models';
import { ActivatedRoute } from '@angular/router';
import {
	Node,
	User,
	TierClass,
	SecondaryUser,
	AppConstants,
} from '../_models/models';
//import {MatSliderModule} from '@angular/material/slider';
import { Router } from '@angular/router';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
	selector: 'app-tier',
	templateUrl: './tier.component.html',
})
export class TierComponent {
	GETAPI = AppConstants.GETURL;
	POSTAPI = AppConstants.POSTURL;

	constructor(
		private route: ActivatedRoute,
		private httpRequests: HttpRequestsService,
		private router: Router
	) {
		if (localStorage.getItem('currentUser')) {
			let user = new User('', '', '');
			user = JSON.parse(localStorage.getItem('currentUser'));
			if (user.userType != 'ADMIN' && user.userType != 'SU') {
				this.router.navigate(['/']);
			} else {
				this.route.params.subscribe((params) => {
					this.tierID = params.id;
					if (this.tierID.toLowerCase() == 'newtierclass') {
						this.isNewTierClass = true;
					} else {
						this.isExistingTier = true;
					}
					if (this.isExistingTier) {
						this.httpRequests.getTierClassID(this.tierID).subscribe(
							(data) => {
								if (data['status'] == '1') {
									this.model = data['tierClass'];
									//console.log(result['tierClass']);
									if (
										this.model.tierUpperBand / this.MEGA >
										1000
									) {
										this.model.tierUpperBand =
											this.model.tierUpperBand /
											this.GIGA;
										this.model.tierLowerBand =
											this.model.tierLowerBand /
											this.GIGA;
										this.model.range = 'GHz';
									} else {
										this.model.tierUpperBand =
											this.model.tierUpperBand /
											this.MEGA;
										this.model.tierLowerBand =
											this.model.tierLowerBand /
											this.MEGA;
										this.model.range = 'MHz';
									}
								}
							},
							(error) => console.error(error)
						);
					}
				});
			}
		}
		/*this.route.params.subscribe(params => this.instrument = params.instrument);
      let str = this.instrument.replace(/\s/g, "%20");
      this.http.get<Student[]>(this.GETAPI + '?action=getStudentsByInstrument&instrument='+str).subscribe(data => {
        if(data['message'] == "No Students"){
          this.students = [];
        }
        else{
            this.students = data;
        }
    }, error => console.error(error));*/
	}

	creatorID = '';
	tierPriorityLevels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
	maxTierNumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
	ranges = ['MHz', 'GHz'];
	GIGA = 1000000000;
	MEGA = 1000000;

	isNewTierClass = false;
	isExistingTier = false;
	tierID = '';
	model = new TierClass(null, null, null, null, null, null, null, 'MHz');

	submitted = false;

	onSubmitNew() {
		this.submitted = true;
		var user = JSON.parse(localStorage.getItem('currentUser'));

		this.httpRequests.createTierClass(this.model, this.GIGA, this.MEGA).subscribe(
			(data) => {
				if (data['status'] == '1') {
					this.router.navigate(['/tiers/showAll']);
				}
			},
			(error) => console.error(error)
		);
	}
	onSubmitExisting() {
		this.submitted = true;
		var user = JSON.parse(localStorage.getItem('currentUser'));

		this.httpRequests.updateTierClass(this.model).subscribe(
			(data) => {
				if (data['status'] == '1') {
					this.router.navigate(['/tiers/showAll']);
				}
			},
			(error) => console.error(error)
		);
	}

	// TODO: Remove this when we're done
	get diagnostic() {
		return JSON.stringify(this.model);
	}

	newTierClass() {
		this.model = new TierClass(
			null,
			null,
			null,
			null,
			null,
			null,
			null,
			'MHz'
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
	public updateBands() {
		if (this.model.tierUpperBand < this.model.tierLowerBand) {
			this.model.tierUpperBand = this.model.tierLowerBand;
		}
	}

	public cancel() {
		this.router.navigate(['/tiers/showAll']);
	}
}
