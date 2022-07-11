// tslint:disable: indent
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import 'rxjs/add/observable/throw';
import 'rxjs/add/operator/catch';
import {
	User,
	AppConstants,
	Director,
	PrimaryUser,
	SecondaryUser,
	GrantRequest,
} from '../_models/models';

@Injectable({
	providedIn: 'root',
})
export class HttpRequestsService {
	public currentUser: Observable<User>;
	POSTAPI = AppConstants.POSTURL;
	GETAPI = AppConstants.GETURL;

	SERVER = AppConstants.BACKEND;
	HEEADERS = new HttpHeaders({
		'Content-Type':'application/json',
		'Access-Control-Allow-Origin': '*'
	});

	constructor(private httpClient: HttpClient) {}

	public adminLogin(model: any): Observable<any> {
		var body = JSON.stringify({
			password: model.password,
			username: model.username
		});

		return this.httpClient.post(this.SERVER + "adminLogin", body, {headers: this.HEEADERS});
	}

	public getPrimaryUsers(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getPrimaryUsers');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public getSecondaryUsers(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getSecondaryUsers');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params, {
			observe: 'response',
			headers: { 'Content-Type': 'application/json' }, });
	}

	public getAllNodes(): Observable<any> {
		return this.httpClient.get(this.SERVER + "nodes", {headers: this.HEEADERS});
	}

	public getMyNodes(SUId: string): Observable<any> {
		let params = new HttpParams();
		params = params.set('SUID', SUId);
		params = params.set('action', 'getAllNodes');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public logGrant(grantID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'logGrant');
		params = params.set('grantID', grantID.toString());
		params = params.set('status', 'DELETED');

		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public createSecondaryAccount(model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'createSU');
		params = params.set('secondaryUserName', model.secondaryUserName);
		params = params.set('secondaryUserEmail', model.secondaryUserEmail);
		params = params.set(
			'secondaryUserPassword',
			model.secondaryUserPassword
		);
		params = params.set('nodeID', model.nodeID);
		params = params.set('deviceID', model.deviceID);
		params = params.set('location', model.location);
		const body = new FormData();
		body.append('action', 'createSU');
		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public createJudge(model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'createJudge');
		params = params.set('title', model.title);
		params = params.set('firstName', model.firstName);
		params = params.set('lastName', model.lastName);
		params = params.set('email', model.email);
		params = params.set('phone', model.phone);
		params = params.set('password', model.password);
		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public createNode(model: any) {
		let params = new HttpParams();
		params = params.set('action', 'createNode');
		params = params.set('nodeName', model.nodeName.toString());
		params = params.set('location', model.location);
		params = params.set('IPAddress', model.IPAddress);
		params = params.set('trustLevel', model.trustLevel.toString());
		params = params.set('minFrequency', model.minFrequency.toString());
		params = params.set('maxFrequency', model.maxFrequency.toString());
		params = params.set('minSampleRate', model.minSampleRate.toString());
		params = params.set('maxSampleRate', model.maxSampleRate.toString());
		params = params.set('nodeType', model.nodeType);
		params = params.set('mobility', model.mobility.toString());
		params = params.set('status', model.status);
		params = params.set('comment', model.comment.toString());
		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public createRequest(model: GrantRequest, isAdmin: boolean): Observable<any> {
		let MHz = 10000000;
		let user = JSON.parse(localStorage.getItem('currentUser'));

		let params = new HttpParams();
		params = params.set('action', 'createRequest');
		if (isAdmin) {
			params = params.set(
				'secondaryUserID',
				model.secondaryUserID.toString()
			);
		} else {
			user = new User('', '', '');
			user = JSON.parse(localStorage.getItem('currentUser'));
			params = params.set('secondaryUserID', user.id.toString());
		}
		params = params.set('nodeName', 'namePlaceholder');
		params = params.set('location', model.location);
		params = params.set('minFrequency', (MHz * model.minFrequency).toString());
		params = params.set('maxFrequency', (MHz * model.maxFrequency).toString());
		params = params.set(
			'preferredFrequency',
			(MHz * model.preferredFrequency).toString()
		);
		params = params.set(
			'frequencyAbsolute',
			model.frequencyAbsolute.toString()
		);
		params = params.set('minBandwidth', model.minBandwidth.toString());
		params = params.set(
			'preferredBandwidth',
			model.preferredBandwidth.toString()
		);
		params = params.set('startTime', model.startTime.toString());
		params = params.set('endTime', model.endTime.toString());
		params = params.set(
			'approximateByteSize',
			model.approximateByteSize.toString()
		);
		params = params.set('dataType', model.dataType);
		params = params.set('powerLevel', model.powerLevel.toString());
		params = params.set('mobility', model.mobility.toString());
		params = params.set('maxVelocity', model.maxVelocity.toString());

		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public createNodeRequest(model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'createNode');
		params = params.set('nodeName', model.secondaryUserID.toString());
		params = params.set('location', model.location);
		params = params.set('minFrequency', model.minFrequency.toString());
		params = params.set('maxFrequency', model.maxFrequency.toString());
		params = params.set(
			'preferredFrequency',
			model.preferredFrequency.toString()
		);
		params = params.set(
			'frequencyAbsolute',
			model.frequencyAbsolute.toString()
		);
		params = params.set('minBandwidth', model.minBandwidth.toString());
		params = params.set(
			'preferredBandwidth',
			model.preferredBandwidth.toString()
		);
		params = params.set('startTime', model.startTime.toString());
		params = params.set('endTime', model.endTime.toString());
		params = params.set(
			'approximateByteSize',
			model.approximatelyByteSize.toString()
		);
		params = params.set('dataType', model.dataType);
		params = params.set('powerLevel', model.powerLevel.toString());
		params = params.set('mobility', model.mobility.toString());
		params = params.set('maxVelocity', model.maxVelocity.toString());

		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public checkEmail(model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'checkEmailAvail');
		params = params.set('email', model.secondaryUserEmail);
		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public getSpectrumGrants(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getSpectrumGrants');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public getGrantByID(grantID: string) {
		let params = new HttpParams();
		params = params.set('action', 'getSpectrumGrant');
		params = params.set('grantID', grantID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}
	
	public getGrantLogs(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getGrantLogs');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public getGrantLogByID(grantID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getGrantLogs');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);
		params = params.set('grantID', grantID.toString());

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public getRegionSchedules(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getRegionSchedules');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}
	
	public getGrantRequests(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getGrantRequests');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);
		
		return this.httpClient.post(this.GETAPI, params);
	}
	
	public suLogin(model: any): Observable<any> {
		var body = JSON.stringify({
			password: model.password,
			username: model.username
		});

		return this.httpClient.post(this.SERVER + "suLogin", body, {headers: this.HEEADERS});
	}

	public getNodeByID(nodeID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getNode');
		params = params.set('nodeID', nodeID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public createRegionSchedule(model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'createRegionSchedule');
		params = params.set('regionName', model.regionName);
		params = params.set('regionShape', model.regionShape);
		params = params.set('shapeRadius', model.shapeRadius.toString());
		params = params.set('shapePoints', model.shapePoints);
		params = params.set('schedulingAlgorithm', model.schedulingAlgorithm);
		params = params.set('useSUTiers', model.useSUTiers.toString());
		params = params.set('useClassTiers', model.useClassTiers.toString());
		params = params.set(
			'useInnerClassTiers',
			model.useInnerClassTiers.toString()
		);
		params = params.set('isDefault', model.isDefault.toString());
		params = params.set('isActive', model.isActive.toString());

		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public updateTierClass(model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'updateTierClass');
		params = params.set('tierClassID', model.tierClassID);
		params = params.set('tierClassName', model.tierClassName.toString());
		params = params.set(
			'tierPriorityLevel',
			model.tierPriorityLevel.toString()
		);
		params = params.set('tierClassDescription', model.tierClassDescription);
		params = params.set('maxTierNumber', model.maxTierNumber.toString());
		params = params.set('tierUpperBand', model.tierUpperBand.toString());
		params = params.set('tierLowerBand', model.tierLowerBand.toString());

		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public updateRegionSchedule(model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'updateRegionSchedule');
		params = params.set('regionID', model.regionID);
		params = params.set('regionName', model.regionName);
		params = params.set('regionShape', model.regionShape);
		params = params.set('shapeRadius', model.shapeRadius.toString());
		params = params.set('shapePoints', model.shapePoints);
		params = params.set('schedulingAlgorithm', model.schedulingAlgorithm);
		params = params.set('useSUTiers', model.useSUTiers.toString());
		params = params.set('useClassTiers', model.useClassTiers.toString());
		params = params.set(
			'useInnerClassTiers',
			model.useInnerClassTiers.toString()
		);
		params = params.set('isDefault', model.isDefault.toString());
		params = params.set('isActive', model.isActive.toString());

		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public updateNode(model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'updateNode');
		params = params.set('nodeID', model.nodeID.toString());
		params = params.set('nodeName', model.nodeName.toString());
		params = params.set('location', model.location);
		params = params.set('IPAddress', model.IPAddress);
		params = params.set('trustLevel', model.trustLevel.toString());
		params = params.set('minFrequency', model.minFrequency.toString());
		params = params.set('maxFrequency', model.maxFrequency.toString());
		params = params.set('minSampleRate', model.minSampleRate.toString());
		params = params.set('maxSampleRate', model.maxSampleRate.toString());
		params = params.set('nodeType', model.nodeType);
		params = params.set('mobility', model.mobility.toString());
		params = params.set('status', model.status);
		params = params.set('comment', model.comment.toString());
		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public getPrimaryUserByID(userID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getPrimaryUser');
		params = params.set('primaryUserID', userID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}
	
	public getPrimaryUserActivityByID(userID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getPrimaryUserActivitiesByPUID');
		params = params.set('primaryUserID', userID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public getSecondaryUserByID(userID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getSecondaryUser');
		params = params.set('secondaryUserID', userID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public createTierClass(
		model: any,
		GIGA: number,
		MEGA: number
	): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'createTierClass');
		params = params.set('tierClassName', model.tierClassName.toString());
		params = params.set(
			'tierPriorityLevel',
			model.tierPriorityLevel.toString()
		);
		params = params.set('tierClassDescription', model.tierClassDescription);
		params = params.set('maxTierNumber', model.maxTierNumber.toString());
		// tslint:disable-next-line: triple-equals
		if (model.range == 'MHz') {
			params = params.set(
				'tierUpperBand',
				(model.tierUpperBand * MEGA).toString()
			);
			params = params.set(
				'tierLowerBand',
				(model.tierLowerBand * MEGA).toString()
			);
		} else {
			params = params.set(
				'tierUpperBand',
				(model.tierUpperBand * GIGA).toString()
			);
			params = params.set(
				'tierLowerBand',
				(model.tierLowerBand * GIGA).toString()
			);
		}

		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public getTierClassID(tierID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getTierClass');
		params = params.set('tierClassID', tierID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public getSUsNotInTierClassByID(tierID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getSUsNotInTierClass');
		params = params.set('tierClassID', tierID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public deleteTierClassAssignmentsByID(secondaryUser: any): Observable<any> {
		let params = new HttpParams();
        params = params.set('action',  'deleteTierClassAssignment');
        params = params.set('assignmentID',  secondaryUser.tierAssignmentID);
        return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public getTierClass(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getTierClasses');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params)
		.catch(this.handleError);
	}

	public alterTierClassAssignmentByID(tierID: any, model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action',  'alterTierClassAssignment');
		params = params.set('secondaryUserID',  model.secondaryUserID);
		params = params.set('tierClassID', tierID);
		params = params.set('innerTierLevel', model.innerTierLevel.toString());
		params = params.set('isNewTA', true.toString());
		return this.httpClient.post(this.POSTAPI, params).catch(this.handleError);
	}

	public getAllGrantsBySUID(userID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getAllGrantsBySUID');
		params = params.set('SUID', userID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.httpClient.post(this.GETAPI, params).catch(this.handleError);
	}

	public deleteGrantRequest(grantRequest: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'deleteGrantRequest');
		params = params.set('grantRequestID', grantRequest.requestID);

		return this.httpClient.post(this.POSTAPI, params);
	}

	private handleError(error: Response) {
		return Observable.throw(error);
	}
}
