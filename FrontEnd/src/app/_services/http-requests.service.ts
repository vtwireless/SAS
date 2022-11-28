// tslint:disable: indent
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
// import 'rxjs/add/observable/throw';
// import 'rxjs/add/operator/catch';

import { User, AppConstants, GrantRequest, RequestMethod, RequestProtocol } from '../_models/models';
import { SocketService } from './socket.service';


@Injectable({
	providedIn: 'root',
})

export class HttpRequestsService {
	public currentUser: Observable<User>;
	private defaultProtocol = RequestProtocol.HTTP;
	private NotImplementedError = throwError("Method not implemented");

	HEADERS = new HttpHeaders({
		'Content-Type': 'application/json',
		'Access-Control-Allow-Origin': '*'
	});
	RESTURL = AppConstants.SERVER_HOSTNAME + ":" + AppConstants.SERVER_PORT + "/"

	constructor(
		private httpClient: HttpClient,
		private socketClient: SocketService
	) {
		this.socketClient.configure(AppConstants.SERVER_HOSTNAME, AppConstants.SERVER_PORT);
	}


	private sendRequests(
		reqProtocol: RequestProtocol, reqMethod: RequestMethod, reqCode: string, reqBody: any, resCode: string
	): Observable<any> {
		/**
		 * Common Method for sending requests to backend server. Returns an observable
		 */

		if (reqProtocol == RequestProtocol.SOCKET) {
			this.socketClient.emit(reqCode, reqBody);

			return this.socketClient.listen(resCode);
		}

		else if (reqProtocol == RequestProtocol.HTTP) {
			let url = `${this.RESTURL}${reqCode}`;

			if (reqMethod == RequestMethod.GET) {
				return this.httpClient.get(url, { headers: this.HEADERS });
			} else if (reqMethod == RequestMethod.POST) {
				return this.httpClient.post(url, reqBody, { headers: this.HEADERS })
			}
		}
	}

	// ------------------------------ User Requests ------------------------------------

	public suLogin(model: any): Observable<any> {
		var body = {
			password: model.password,
			username: model.username
		};

		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, 'suLogin', body, 'suLoginResponse'
		);
	}

	public adminLogin(model: any): Observable<any> {
		var body = {
			password: model.password,
			username: model.username
		};
		
		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, 'adminLogin', body, 'adminLoginResponse'
		);
	}

	public createSecondaryAccount(model: any): Observable<any> {
		var body = {
			secondaryUserName: model.secondaryUserName,
			secondaryUserEmail: model.secondaryUserEmail,
			secondaryUserPassword: model.secondaryUserPassword,
			nodeID: model.nodeID,
			deviceID: model.deviceID,
			location: model.location,
		};

		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, 'createSU', body, 'createSUResponse'
		);
	}

	public getSecondaryUsers(): Observable<any> {
		return this.sendRequests(
			this.defaultProtocol, RequestMethod.GET, 'getUsers', {}, 'getUsersResponse'
		);
	}

	public getPrimaryUsers(): Observable<any> {
		return this.sendRequests(
			this.defaultProtocol, RequestMethod.GET, 'getUsers', {}, 'getUsersResponse'
		);
	}
	
	public checkEmail(model: any): Observable<any> {
		var body = JSON.stringify({
			email: model.secondaryUserEmail
		});

		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, "checkEmailAvail", body, "checkEmailAvailResponse"
		);
	}

	// ------------------------------ User Tier Class Requests -----------------------------------

	public createTierClass(
		model: any,
		GIGA: number,
		MEGA: number
	): Observable<any> {
		var scale = model.range == 'MHz' ? MEGA : GIGA;
		var body = {
			tierClassName: model.tierClassName,
			tierPriorityLevel: model.tierPriorityLevel,
			tierClassDescription: model.tierClassDescription,
			maxTierNumber: model.maxTierNumber,
			tierUpperBand: model.tierUpperBand * scale,
			tierLowerBand: model.tierLowerBand * scale
		};

		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, "createTierClass", body, 'createTierClassResponse'
		);
	}

	public getTierClassID(tierID: any): Observable<any> {
		let body = { 'tierClassID': tierID };
		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, 'getTierClassById', body, 'getTierClassByIdResponse'
		);
	}

	public getTierClass(): Observable<any> {
		return this.sendRequests(
			this.defaultProtocol, RequestMethod.GET, 'getTierClass', {}, 'getTierClassResponse'
		);
	}

	// ------------------------------ Spectrum Inquiry Requests -----------------------------------

	public spectrumInqRequest(model: any) {
		var body = {
			spectrumInquiryRequest: [{
				cbsdId: parseInt(model.cbsdId),
				inquiredSpectrum: model.inquiredSpectrum
			}]
		};

		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, 'spectrumInquiryRequest', body, 'spectrumInquiryResponse'
		);
	}
	public nodeDeregistrationRequest(model:any){
		var body = {
			deregistrationRequest: [{
				cbsdId: parseInt(model.cbsdId)
			}]
		};

		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, 'deregistrationRequest', body, 'deregistrationResponse'
		);
	}

	public grantRelinquishmentRequest(model:any){
		var body = {
			relinquishmentRequest: [{
				cbsdId: parseInt(model.cbsdId),
				grantId: parseInt(model.grantId)
			}]
		}

		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, 'relinquishmentRequest', body, 'relinquishmentResponse'
		);

	}

	// ------------------------------ Node Requests ------------------------------------

	public createNode(model: any) {
		var body = {
			registrationRequest: [{
				nodeName: model.nodeName.toString(),
				location: model.location,
				IPAddress: model.IPAddress,
				trustLevel: model.trustLevel.toString(),
				minFrequency: model.minFrequency.toString(),
				maxFrequency: model.maxFrequency.toString(),
				minSampleRate: model.minSampleRate.toString(),
				maxSampleRate: model.maxSampleRate.toString(),
				nodeType: model.nodeType,
				mobility: model.mobility.toString(),
				status: model.status,
				comment: model.comment.toString(),
				userId: model.userId.toString()
			}]
		};

		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, 'registrationRequest', body, 'registrationResponse'
		);
	}

	public getAllNodes(): Observable<any> {
		return this.sendRequests(
			this.defaultProtocol, RequestMethod.GET, 'getNodesRequest', {}, 'getNodesResponse'
		);
	}


	// ------------------------------ Grant Requests -----------------------------------

	public createRequest(model: GrantRequest, isAdmin: boolean): Observable<any> {
		var body = {
			grantRequest: [{
				secondaryUserID: model.secondaryUserID,
				secondaryUserName: model.secondaryUserName,
				location: model.location,
				minFrequency: model.minFrequency,
				maxFrequency: model.maxFrequency,
				preferredFrequency: model.preferredFrequency,
				frequencyAbsolute: model.frequencyAbsolute,
				minBandwidth: model.minBandwidth,
				maxBandwidth: model.maxBandwidth,
				preferredBandwidth: model.preferredBandwidth,
				startTime: model.startTime.toString(),
				endTime: model.endTime.toString(),
				approximateByteSize: model.approximateByteSize,
				dataType: model.dataType,
				powerLevel: model.powerLevel,
				mobility: model.mobility,
				maxVelocity: model.maxVelocity,
				range: model.range,
				cbsdId: model.cbsdId
			}]
		};

		return this.sendRequests(
			this.defaultProtocol, RequestMethod.POST, 'grantRequest', body, 'grantResponse'
		);
	}

	public getSpectrumGrants(): Observable<any> {
		return this.sendRequests(
			this.defaultProtocol, RequestMethod.GET, 'getGrantsRequest', {}, 'getGrantsResponse'
		);

	}

	// ------------------------------ Todo Requests ------------------------------------

	public getMyNodes(SUId: string): Observable<any> {
		let params = new HttpParams();
		params = params.set('SUID', SUId);
		params = params.set('action', 'getAllNodes');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.GET, "", {}, ""
		// );
	}

	public logGrant(grantID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'logGrant');
		params = params.set('grantID', grantID.toString());
		params = params.set('status', 'DELETED');

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
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

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public createSpectrumInquiryRequest(model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'spectrumInqRequest');
		params = params.set('cbsdId', model.cbsdId.toString());
		params = params.set('selectedFrequencyRanges', model.selectedFrequencyRanges);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
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

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public getGrantByID(grantID: string) {
		let params = new HttpParams();
		params = params.set('action', 'getSpectrumGrant');
		params = params.set('grantID', grantID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.GET, "", {}, ""
		// );
	}

	public getGrantLogs(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getGrantLogs');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.GET, "", {}, ""
		// );
	}

	public getGrantLogByID(grantID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getGrantLogs');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);
		params = params.set('grantID', grantID.toString());

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.GET, "", {}, ""
		// );
	}

	public getRegionSchedules(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getRegionSchedules');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.GET, "", {}, ""
		// );
	}

	public getGrantRequests(): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getGrantRequests');
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.GET, "", {}, ""
		// );
	}

	public getNodeByID(nodeID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getNode');
		params = params.set('nodeID', nodeID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.GET, "", {}, ""
		// );
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

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
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

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
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

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
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

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public getPrimaryUserByID(userID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getPrimaryUser');
		params = params.set('primaryUserID', userID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public getPrimaryUserActivityByID(userID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getPrimaryUserActivitiesByPUID');
		params = params.set('primaryUserID', userID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public getSecondaryUserByID(userID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getSecondaryUser');
		params = params.set('secondaryUserID', userID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public getSUsNotInTierClassByID(tierID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getSUsNotInTierClass');
		params = params.set('tierClassID', tierID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public deleteTierClassAssignmentsByID(secondaryUser: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'deleteTierClassAssignment');
		params = params.set('assignmentID', secondaryUser.tierAssignmentID);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public alterTierClassAssignmentByID(tierID: any, model: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'alterTierClassAssignment');
		params = params.set('secondaryUserID', model.secondaryUserID);
		params = params.set('tierClassID', tierID);
		params = params.set('innerTierLevel', model.innerTierLevel.toString());
		params = params.set('isNewTA', true.toString());

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public getAllGrantsBySUID(userID: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'getAllGrantsBySUID');
		params = params.set('SUID', userID);
		params = params.set('SAS_KEY', AppConstants.SAS_KEY);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}

	public deleteGrantRequest(grantRequest: any): Observable<any> {
		let params = new HttpParams();
		params = params.set('action', 'deleteGrantRequest');
		params = params.set('grantRequestID', grantRequest.requestID);

		return this.NotImplementedError;

		// return this.sendRequests(
		// 	this.defaultProtocol, RequestMethod.POST, "", {}, ""
		// );
	}
}
