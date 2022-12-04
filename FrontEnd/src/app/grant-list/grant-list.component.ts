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
import {MatSort} from '@angular/material/sort';


@Component({
	selector: 'app-grant-list',
	templateUrl: './grant-list.component.html',
	styleUrls: ['./grant-list.component.css']
})
export class GrantListComponent implements AfterViewInit {
	SpectrumGrants: GrantList[] = [];
	displayStyle = "none";
	GrantRequests: Array<GrantRequest> = [];
	currentGrantRequest: GrantList;

	API = AppConstants.GETURL;
	public logged = false;
	public active = false;
	public requests = false;
	public type = '';
	MEGA = 1000000;
	GIGA = 1000000000;

	dataSource = new MatTableDataSource<GrantList>(this.SpectrumGrants);
	// sortedData: GrantList[];
	@ViewChild(MatPaginator, { static: false }) paginator: MatPaginator;
	@ViewChild(MatSort, { static: false }  ) sort: MatSort;

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
											cbsdId:grant.cbsdId,
											approximateByteSize:grant.approximateByteSize,
											secondaryUserID: grant.secondaryUserID,
											dataType:grant.dataType,
											frequency: (grant.minFrequency/1000000).toString() + " - " + (grant.maxFrequency/1000000).toString(),
											minBandwidth: grant.minBandwidth,
											preferredBandwidth: grant.preferredBandwidth,
											startTime: grant.startTime,
											endTime: grant.endTime,
											frequencyAbsolute:grant.frequencyAbsolute,
											status: grant.status,
											location: grant.location,
											maxVelocity:grant.maxVelocity,
											mobility:grant.mobility,
											powerLevel:grant.powerLevel,
											preferredFrequency:grant.preferredFrequency,
											range:grant.range,
											tier:grant.tier,
											secondaryUserName:grant.secondaryUserName
										}

										this.SpectrumGrants.push(grant_obj); 
									}
								}
								this.dataSource.data = this.SpectrumGrants;
								// this.sortedData = this.dataSource.data.slice();
							},
							(error) => console.error(error)
						);

				});
			}
		}
	}

	ngAfterViewInit() {
		this.dataSource.paginator = this.paginator;
		this.dataSource.sort = this.sort;
		console.log(this.dataSource);
	}


	openPopup(grantId) {
		this.displayStyle = "block";

		for(let i=0;i<this.SpectrumGrants.length;i++){
			if(this.SpectrumGrants[i]['grantId']===grantId){
				console.log("here");
				this.currentGrantRequest = this.SpectrumGrants[i];
			}
		}

		console.log(this.currentGrantRequest);

	}
	closePopup() {
		this.displayStyle = "none";
	}



	// sortData(sort:Sort){
	// 	const data = this.dataSource.data.slice();
	//
	// 	if (!sort.active || sort.direction === '') {
	// 		this.sortedData = data;
	// 		return;
	// 	}
	//
	// 	this.sortedData = data.sort((a, b) => {
	// 		const isAsc = sort.direction === 'asc';
	// 		switch (sort.active) {
	// 			case 'grantId':
	// 				return this.compare(a.grantId, b.grantId, isAsc);
	// 			default:
	// 				return 0;
	// 		}
	// 	});
	// }
	//
	// compare(a: number | string, b: number | string, isAsc: boolean) {
	// 	return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
	// }




}


export interface GrantList {
	grantId: any;
	approximateByteSize:any;
	secondaryUserID: any;
	frequency: any;
	cbsdId:any;
	dataType:any;
	minBandwidth: any;
	preferredBandwidth: any;
	startTime: any;
	endTime: any;
	powerLevel:any;
	mobility:any;
	frequencyAbsolute:any;
	status: any;
	location: any;
	tier:any;
	secondaryUserName:any;
	range:any;
	preferredFrequency:any;
	maxVelocity:any;
}
