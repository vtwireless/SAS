import { AfterViewInit, Component, Inject, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import {
	PrimaryUser,
	SecondaryUser,
	SpectrumGrant,
	GrantRequest,
	User,
	AppConstants,
} from '../_models/models';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
	selector: 'app-grant-list',
	templateUrl: './grant-list.component.html',
	styleUrls: ['./grant-list.component.css']
})
export class GrantListComponent implements AfterViewInit {
	SpectrumGrants: GrantList[] = [];
	GrantRequests: Array<GrantRequest> = [];
	API = AppConstants.GETURL;
	public logged = false;
	public active = false;
	public requests = false;
	public type = '';
	MEGA = 1000000;
	GIGA = 1000000000;

	dataSource = new MatTableDataSource<GrantList>(this.SpectrumGrants);
	@ViewChild(MatPaginator, { static: false }) paginator: MatPaginator;

	displayedColumns: string[] = [
		'grantId', 'secondaryUserID', 'frequency', 'minBandwidth', 'preferredBandwidth', 'startTime',
		'endTime', 'status', 'location'
	];

	constructor(
		private httpRequests: HttpRequestsService,
		private route: ActivatedRoute,
		@Inject('BASE_URL') baseUrl: string,
		router: Router
	) {
		if (localStorage.getItem('currentUser')) {
			let user = new User('', '', '');
			user = JSON.parse(localStorage.getItem('currentUser'));

			if (user.userType != 'ADMIN') {
				router.navigate(['/']);
			} else {
				this.route.params.subscribe((params) => {
					this.type = params.type;
					this.active = false;
					this.logged = false;
					this.requests = false;
					if (this.type == 'active') {
						this.active = true;
					} else if (this.type == 'logged') {
						this.logged = true;
					} else if (this.type == 'requests') {
						this.requests = true;
					}
					// if (this.active) {
						this.httpRequests.getSpectrumGrants().subscribe(
							(data) => {
								if (data['status'] == '1') {
									for (const grant of data['spectrumGrants']) {
										var grant_obj: GrantList = {
											grantId: grant.grantId,
											secondaryUserID: grant.secondaryUserID,
											frequency: grant.maxFrequency.toString() + " - " + grant.minFrequency.toString(),
											minBandwidth: grant.minBandwidth,
											preferredBandwidth: grant.preferredBandwidth,
											startTime: grant.startTime,
											endTime: grant.endTime,
											status: grant.status,
											location: grant.location
										}

										this.SpectrumGrants.push(grant_obj); 
									}
								}
								this.dataSource.data = this.SpectrumGrants;
							},
							(error) => console.error(error)
						);
					// }
					// else if (this.logged) {
					// 	this.httpRequests.getGrantLogs().subscribe(
					// 		(data) => {
					// 			if (data['status'] == '1') {
					// 				this.SpectrumGrants = data['grantLogs'];
					// 			}
					// 		},
					// 		(error) => console.error(error)
					// 	);
					// }
					// else if (this.requests) {
					// 	this.httpRequests.getGrantRequests().subscribe(
					// 		(data) => {
					// 			if (data['status'] == '1') {
					// 				this.GrantRequests = data['grantRequests'];
					// 				for (
					// 					var i = 0;
					// 					i < this.GrantRequests.length;
					// 					i++
					// 				) {
					// 					if (
					// 						this.GrantRequests[i].maxFrequency /
					// 						this.MEGA >
					// 						1000
					// 					) {
					// 						this.GrantRequests[i].maxFrequency =
					// 							this.GrantRequests[i]
					// 								.maxFrequency / this.GIGA;
					// 						this.GrantRequests[i].minFrequency =
					// 							this.GrantRequests[i]
					// 								.minFrequency / this.GIGA;
					// 						this.GrantRequests[
					// 							i
					// 						].preferredFrequency =
					// 							this.GrantRequests[i]
					// 								.preferredFrequency /
					// 							this.GIGA;
					// 						this.GrantRequests[i].range = 'GHz';
					// 					} else {
					// 						this.GrantRequests[i].maxFrequency =
					// 							this.GrantRequests[i]
					// 								.maxFrequency / this.MEGA;
					// 						this.GrantRequests[i].minFrequency =
					// 							this.GrantRequests[i]
					// 								.minFrequency / this.MEGA;
					// 						this.GrantRequests[
					// 							i
					// 						].preferredFrequency =
					// 							this.GrantRequests[i]
					// 								.preferredFrequency /
					// 							this.MEGA;
					// 						this.GrantRequests[i].range = 'MHz';
					// 					}
					// 				}
					// 			}
					// 		},
					// 		(error) => console.error(error)
					// 	);
					// }
				});
			}
		}
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		console.log(this.dataSource);
	}
}

export interface GrantList {
	grantId: any;
	secondaryUserID: any;
	frequency: any;
	minBandwidth: any;
	preferredBandwidth: any;
	startTime: any;
	endTime: any;
	status: any;
	location: any;
}
