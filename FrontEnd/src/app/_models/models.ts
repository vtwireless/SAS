export class AppConstants {
    public static ROOTURL = "http://localhost/SASAPI/";
    public static GETURL = `${AppConstants.ROOTURL}SAS_API_GET.php`;
    public static POSTURL = `${AppConstants.ROOTURL}SAS_API.php`;
    public static SAS_KEY = "qowpe029348fuqw9eufhalksdjfpq3948fy0q98ghefqi";

    public static SERVER_HOSTNAME = 'http://localhost'
	public static SERVER_PORT = '8000'
}

export class SecondaryUser {

    constructor(
        public secondaryUserID: string,
        public secondaryUserEmail: string,
        public secondaryUserPassword: string,
        public secondaryUserName: string,
        public tier: string,
        public nodeID: string,
        public deviceID: string,
        public location: string,
        public passwordb: string,
    ) { }

}

export class SpectrumGrant {

    constructor(
        public grantID: number,
        public approved: string,
        public secondaryUserID: string,
        public secondaryUserName: string,
        public tier: string,
        public deviceID: string,
        public nodeID: string,
        public frequency: number,
        public bandwidth: string,
        public startTime: string,
        public endTime: string,
        public status: string,
        public requestMinFrequency: number,
        public requestMaxFrequency: number,
        public requestPreferredFrequency: number,
        public requestFrequencyAbsolute: number,
        public minBandwidth: number,
        public preferredBandwidth: number,
        public requestStartTime: string,
        public requestEndTime: string,
        public requestApproximatelyByteSize: number,
        public requestDataType: string,
        public requestPowerLevel: number,
        public requestLocation: string,
        public requestMobility: boolean,
        public requestMaxVelocity: number,
        public range: string,
    ) { }

}

export class GrantLog {

    constructor(
        public grantLogID: number,
        public approved: string,
        public secondaryUserID: string,
        public secondaryUserName: string,
        public tier: string,
        public frequency: number,
        public bandwidth: string,
        public startTime: string,
        public endTime: string,
        public status: string,
        public requestMinFrequency: number,
        public requestMaxFrequency: number,
        public requestPreferredFrequency: number,
        public requestFrequencyAbsolute: number,
        public minBandwidth: number,
        public preferredBandwidth: number,
        public requestStartTime: string,
        public requestEndTime: string,
        public requestApproximatelyByteSize: number,
        public requestDataType: string,
        public requestPowerLevel: number,
        public requestLocation: string,
        public requestMobility: boolean,
        public requestMaxVelocity: number,
        public range: string,
    ) { }

}

export class GrantRequest {
    public requestID: number;
    public cbsdId: number;
    public secondaryUserID: string;
    public secondaryUserName: string;
    public tier: string;
    public minFrequency: number;
    public maxFrequency: number;
    public preferredFrequency: number;
    public frequencyAbsolute: boolean;
    public minBandwidth: number;
    public preferredBandwidth: number;
    public startTime: string;
    public endTime: string;
    public approximateByteSize: number;
    public dataType: string;
    public powerLevel: number;
    public location: string;
    public mobility: boolean;
    public maxVelocity: number;
    public range: string;
}

export class Heartbeat {

    constructor(
        public heartbeatID: number,
        public grantID: string,
        public secondaryUserName: string,
        public heartbeatTime: string,
        public secondaryUserLocation: number,
        public secondaryuserVelocity: number,
        public heartbeatGrantStatus: number,
        public heartbeatBandwidth: number,
    ) { }

}
export class SpectrumInquiryRequest {
    constructor(
        public cbsdId: number,
        public inquiredSpectrum: freqRange[],
    ) {
    }
}

export class freqRange {
    constructor(
        public lowFrequency: number,
        public highFrequency: number

    ) {
    }
}

export class Node {

    constructor(
        public nodeID: number,
        public nodeName: string,
        public location: string,
        public trustLevel: number,
        public IPAddress: string,
        public minFrequency: number,
        public maxFrequency: number,
        public minSampleRate: number,
        public maxSampleRate: number,
        public nodeType: string,
        public mobility: boolean,
        public status: string,
        public comment: string,
    ) { }

}

export class PrimaryUser {

    constructor(
        public primaryUserID: number,
        public primaryUserName: string,

    ) { }

}

export class PrimaryUserActivity {
    constructor(
        public PUActivityID: number,
        public primaryUserName: string,
        public primaryUserID: string,
        public frequency: number,
        public bandwidth: number,
        public startTime: string,
        public endTime: string,
        public expectedEndTime: string,
        public location: string,
        public locationConfidence: string,
        public activityStatus: string,
    ) { }
}

export class PrimaryUserLog {
    constructor(
        public PULogID: number,
        public primaryUserID: number,
        public primaryUserName: string,
        public frequency: number,
        public bandwidth: number,
        public startTime: string,
        public endTime: string,
        public expectedEndTime: string,
        public location: string,
        public locationConfidence: number,
        public comment: string,
    ) { }
}

export class Director {

    constructor(
        public directorID: string,
        public title: string,
        public firstName: string,
        public lastName: string,
        public schoolName: string,
        public city: string,
        public phone: string,
        public email: string,
        public password: string,
        public passwordb: string,
        public emailBody: string,
    ) { }

}

export class Judge {

    constructor(
        public id: number,
        public title: string,
        public firstName: string,
        public lastName: string,
        public phone: string,
        public email: string,
        public passwordb: string,
        public password: string,
    ) { }

}

export class Evaluation {

    constructor(
        public id: number,
        public judgeID: string,
        public studentID: string,
        public scaleA: number,
        public scaleB: number,
        public pitch: number,
        public rhythm: number,
        public articulation: number,
        public dynamics: number,
        public expression: number,
        public comments: string,
    ) { }

}

export class Student {

    constructor(
        public studentID: string,
        public firstName: string,
        public lastName: string,
        public instrument: string,
        public grade: number,
        public phone: string,
        public email: string,
        public checkedIn: boolean,
        public rating: number,
        public attending: boolean,
        public invited: boolean,
        public shirtSize: string,
        public highSchool: string,
    ) { }

}

export class JudgedStudent {

    constructor(
        public studentID: string,
        public firstName: string,
        public lastName: string,
        public instrument: string,
        public instrumentb: string,
        public grade: number,
        public phone: string,
        public email: string,
        public checkedIn: boolean,
        public rating: number,
        public invited: boolean,
        public attending: boolean,
        public evaluations: Eval[],
        public directorName: string,
        public highSchool: string,
        public averageScore: number,
        public mouseHover: boolean,
        public shirtSize: string,
        public bandID: string,
    ) { }

}

export class Eval {
    constructor(
        public score: string,
        public judgeName: string,
        public comment: string,
    ) { }
}

export class Band {
    constructor(
        public bandID: string,
        public bandName: string,
        public level: number,
    ) { }
}

export class User {
    constructor(
        public id: string,
        public userType: string,
        public name: string,
    ) { }
}

export class TierClass {
    constructor(
        public tierClassID: string,
        public tierClassName: string,
        public tierPriorityLevel: number,
        public tierClassDescription: string,
        public maxTierNumber: number,
        public tierUpperBand: number,
        public tierLowerBand: number,
        public range: string,
    ) { }

}

export class TierClassAssignment {
    constructor(
        public tierAssignmentID: string,
        public tierClassID: string,
        public tierClassName: string,
        public tierPriorityLevel: number,
        public tierClassDescription: string,
        public maxTierNumber: number,
        public tierUpperBand: number,
        public tierLowerBand: number,
        public secondaryUserID: string,
        public secondaryUserName: string,
        public secondaryUserEmail: string,
        public innerTierLevel: string,
        public range: string,
    ) { }

}

export class Finalization {
    constructor(
        public confirm: string,
        public code: string,
        public action: string,
    ) { }

}

export class RegionScheduler {
    constructor(
        public regionID: string,
        public regionName: string,
        public regionShape: string,
        public shapeRadius: number,
        public shapePoints: string,
        public schedulingAlgorithm: string,
        public useSUTiers: boolean,
        public useClassTiers: boolean,
        public useInnerClassTiers: boolean,
        public isDefault: boolean,
        public isActive: boolean,
        public isShowing: boolean,
        public isEditing: boolean,
        public circle: google.maps.Circle,
        public polygon: google.maps.Polygon,
        public marker: google.maps.Marker,
        public polygonCoordinates: google.maps.LatLng[],
    ) { }
}

export class MapColorConstants {
    public static regionColor = '#FFFF00';
    public static strokeOpacity = 0.8;
    public static strokeWeight = 2;
    public static radioColor = '#DD1111';
    public static SUIcon = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png';
    public static NodeIcon = 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png';
    public static grantIcon = 'http://maps.google.com/mapfiles/ms/icons/green-dot.png';
    public static PUColor = '#FFFFFF';
    public static grantColor = '#11DDAA';
    public static fillOpacity = 0.25;
    public static zero = 0;
}

export class PUMap {
    constructor(
        public primaryUser: PrimaryUser,
        public marker: google.maps.Marker,
    ) { }
}

export class SUMap {
    constructor(
        public secondaryUser: SecondaryUser,
        public marker: google.maps.Marker,
    ) { }
}

export class NodeMap {
    constructor(
        public node: Node,
        public marker: google.maps.Marker,
        public circle: google.maps.Circle,
        public polygon: google.maps.Polygon,
    ) { }
}

export class GrantMap {
    constructor(
        public grant: SpectrumGrant,
        public marker: google.maps.Marker,
        public circle: google.maps.Circle,
        public polygon: google.maps.Polygon,
    ) { }
}

export enum RequestMethod {
    GET = "GET",
    POST = "POST"
}

export enum RequestProtocol {
    HTTP,
    SOCKET
}