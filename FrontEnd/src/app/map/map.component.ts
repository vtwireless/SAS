import { Component, AfterViewInit, ViewChild, ElementRef, Inject } from '@angular/core';
import { PrimaryUser, SecondaryUser, RegionScheduler, Node, SpectrumGrant, User, PUMap, SUMap, NodeMap, GrantMap, AppConstants, MapColorConstants } from '../_models/models';
import { Router, ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
    selector: 'app-map',
    templateUrl: './map.component.html',
    styleUrls: ['./map.component.css']
})
export class MapComponent implements AfterViewInit{

    regionSchedules: Array<RegionScheduler> = [];
    PUs: Array<PUMap> = [];
    SUs: Array<SUMap> = [];
    nodes: Array<NodeMap> = [];
    spectrumGrants: Array<GrantMap> = [];




    showingPUs = true;
    showingSUs = true;
    showingNodes = true;
    showingRegions = true;
    showingGrants = true;

    GETAPI = AppConstants.GETURL;
    POSTAPI = AppConstants.POSTURL;
    MEGA = 1000000;
    GIGA = 1000000000;



    constructor(private httpRequests: HttpRequestsService, private route: ActivatedRoute, @Inject('BASE_URL') baseUrl: string, router: Router) {

        if(localStorage.getItem('currentUser')){
            let user = new User('', '', '');
            user = JSON.parse(localStorage.getItem('currentUser'));
            console.log(user.userType)
            if(user.userType != 'ADMIN' && user.userType != 'SU'){
                router.navigate(['/']);
            }
            else{
                this.httpRequests.getSecondaryUsers().subscribe(data => {
                    if(data['status'] == '1'){
                        for (var j = 0; j< data['secondaryUsers'].length; j++){
                            let temp = new SUMap(data['secondaryUsers'][j], null);
                            this.SUs.push(temp);
                        }
                        for (var i = 0 ; i < this.SUs.length; i++){
                            this.SUs[i].marker = null;
                            var coordinateArray = this.SUs[i].secondaryUser.location.split(',');
                            var coor = new google.maps.LatLng(Number(coordinateArray[0]), Number(coordinateArray[1]));
                            var markerLabel = this.SUs[i].secondaryUser.secondaryUserName;
                            var marker = new google.maps.Marker({
                                position: coor,
                                map: this.map,
                                label: markerLabel,
                                icon: MapColorConstants.SUIcon
                            });
                            this.SUs[i].marker = marker;

                        }
                    }
                }, error => console.error(error));
                this.httpRequests.getAllNodes().subscribe(data => {
                    if(data['status'] == '1'){
                        for (var j = 0; j<data['nodes'].length; j++){
                            let temp = new NodeMap(data['nodes'][j], null, null, null);
                            this.nodes.push(temp);
                        }
                        for (var i = 0 ; i < this.nodes.length; i++){
                            this.nodes[i].marker = null;
                            var coordinateArray = this.nodes[i].node.location.split(',');
                            var coor = new google.maps.LatLng(Number(coordinateArray[0]), Number(coordinateArray[1]));
                            var markerLabel = this.nodes[i].node.nodeName;
                            var marker = new google.maps.Marker({
                                position: coor,
                                map: this.map,
                                label: markerLabel,
                                icon: MapColorConstants.NodeIcon
                            });
                            this.nodes[i].marker = marker;

                        }
                    }
                }, error => console.error(error));
                this.httpRequests.getRegionSchedules().subscribe(data => {
                    if(data['status'] == '1'){
                        this.regionSchedules = data['regionSchedules'];
                        var i = 0;
                        for (i = 0 ; i < this.regionSchedules.length; i++){
                            this.regionSchedules[i].isEditing = false;
                            this.regionSchedules[i].isShowing = false;
                            this.regionSchedules[i].marker = null;
                            var coordinateArray = this.regionSchedules[i].shapePoints.split(',');
                            var coor = new google.maps.LatLng(Number(coordinateArray[0]), Number(coordinateArray[1]));
                            if (this.regionSchedules[i].regionShape == "circle"){
                                this.regionSchedules[i].circle =  new google.maps.Circle({
                                    strokeColor: MapColorConstants.regionColor,
                                    strokeOpacity: MapColorConstants.strokeOpacity,
                                    strokeWeight: MapColorConstants.strokeWeight,
                                    fillColor: MapColorConstants.regionColor,
                                    fillOpacity: MapColorConstants.fillOpacity,
                                    map: this.map,
                                    center: coor,
                                    radius: this.regionSchedules[i].shapeRadius
                                });
                                var markerLabel = this.regionSchedules[i].regionName + ", Radius:" + this.regionSchedules[i].shapeRadius + 'm';
                                var marker = new google.maps.Marker({
                                    position: coor,
                                    map: this.map,
                                    //title: message,
                                    label: markerLabel
                                });
                                this.regionSchedules[i].marker = marker;
                            }
                            else if (this.regionSchedules[i].regionShape == "polygon"){
                                this.regionSchedules[i].polygonCoordinates = [];
                                var coordinatesArray = this.regionSchedules[i].shapePoints.split(',');
                                var totalLat = 0;
                                var totalLong = 0;
                                for (var j = 0; j < coordinateArray.length; j++){
                                    this.regionSchedules[i].polygonCoordinates.push(new google.maps.LatLng(Number(coordinatesArray[j]), Number(coordinatesArray[j+1])));
                                    totalLat = totalLat + Number(coordinatesArray[j]);
                                    totalLong = totalLong + Number(coordinatesArray[j+1]);
                                    j++;
                                }
                                totalLat = totalLat/(coordinateArray.length/2);
                                totalLong = totalLong/(coordinateArray.length/2);
                                var markerLabel = this.regionSchedules[i].regionName;
                                var marker = new google.maps.Marker({
                                    position: new google.maps.LatLng(totalLat, totalLong),
                                    map: this.map,
                                    label: markerLabel
                                });
                                this.regionSchedules[i].marker = marker;

                                this.regionSchedules[i].polygon = new google.maps.Polygon({
                                    strokeColor: MapColorConstants.regionColor,
                                    strokeOpacity: MapColorConstants.strokeOpacity,
                                    strokeWeight: MapColorConstants.strokeWeight,
                                    fillColor: MapColorConstants.regionColor,
                                    fillOpacity: MapColorConstants.fillOpacity,
                                    map: this.map,
                                    paths: this.regionSchedules[i].polygonCoordinates
                                });
                                if (!this.regionSchedules[i].isActive){
                                    this.regionSchedules[i].marker.setMap(null);
                                    if (this.regionSchedules[i].polygon){
                                        this.regionSchedules[i].polygon.setMap(null);
                                    }
                                    if (this.regionSchedules[i].circle){
                                        this.regionSchedules[i].circle.setMap(null);
                                    }
                                }
                            }
                            else {
                                console.log('shape error');
                            }
                            if (!this.regionSchedules[i].isActive){
                                this.regionSchedules[i].marker.setMap(null);
                                if (this.regionSchedules[i].polygon){
                                    this.regionSchedules[i].polygon.setMap(null);
                                }
                                if (this.regionSchedules[i].circle){
                                    this.regionSchedules[i].circle.setMap(null);
                                }
                            }
                        }
                    }
                }, error => console.error(error));

                this.httpRequests.getSpectrumGrants().subscribe(data => {
                    if(data['status'] == '1'){
                        for (var j = 0; j< data['spectrumGrants'].length; j++){
                            let temp = new GrantMap(data['spectrumGrants'][j], null, null, null);
                            this.spectrumGrants.push(temp);
                        }
                        for (var i = 0 ; i < this.spectrumGrants.length; i++){
                            this.spectrumGrants[i].marker = null;
                            var coordinateArray = this.spectrumGrants[i].grant.requestLocation.split(',');
                            var coor = new google.maps.LatLng(Number(coordinateArray[0]), Number(coordinateArray[1]));
                            var markerLabel = this.spectrumGrants[i].grant.secondaryUserName + " " + this.spectrumGrants[i].grant.frequency + 'Hz';
                            this.spectrumGrants[i].marker = new google.maps.Marker({
                                position: coor,
                                map: this.map,
                                label: markerLabel,
                                icon: MapColorConstants.grantIcon
                            });
                            this.spectrumGrants[i].circle =  new google.maps.Circle({
                                    strokeColor: MapColorConstants.grantColor,
                                    strokeOpacity: MapColorConstants.strokeOpacity,
                                    strokeWeight: MapColorConstants.strokeWeight,
                                    fillColor: MapColorConstants.grantColor,
                                    fillOpacity: MapColorConstants.fillOpacity,
                                    map: this.map,
                                    center: coor,
                                    radius: 500
                                });

                        }
                    }
                }, error => console.error(error));

}
}
}

togglePUs(){
    if (this.showingPUs){
        for (var i = 0; i < this.PUs.length; i++){
            this.PUs[i].marker.setMap(null);
        }
    }
    else{
        for (var i = 0; i < this.PUs.length; i++){
            this.PUs[i].marker.setMap(this.map);
        }
    }

    this.showingPUs = !this.showingPUs;
}

toggleSUs(){
    if (this.showingSUs){
        for (var i = 0; i < this.SUs.length; i++){
            this.SUs[i].marker.setMap(null);
        }
    }
    else{
        for (var i = 0; i < this.SUs.length; i++){
            this.SUs[i].marker.setMap(this.map);
        }
    }

    this.showingSUs = !this.showingSUs;
}
toggleNodes(){
    if (this.showingNodes){
        for (var i = 0; i < this.nodes.length; i++){
            this.nodes[i].marker.setMap(null);

            if (this.nodes[i].circle){
                this.nodes[i].circle.setMap(null);
            }
            if (this.nodes[i].polygon){
                this.nodes[i].polygon.setMap(null);
            }
        }
    }
    else{
        for (var i = 0; i < this.nodes.length; i++){
            this.nodes[i].marker.setMap(this.map);
            if (this.nodes[i].circle){
                this.nodes[i].circle.setMap(this.map);
            }
            if (this.nodes[i].polygon){
                this.nodes[i].polygon.setMap(this.map);
            }
        }
    }

    this.showingNodes = !this.showingNodes;
}

toggleRegions(){
    if (this.showingRegions){
        for (var i = 0; i < this.regionSchedules.length; i++){
            this.regionSchedules[i].marker.setMap(null);

            if (this.regionSchedules[i].circle){
                this.regionSchedules[i].circle.setMap(null);
            }
            if (this.regionSchedules[i].polygon){
                this.regionSchedules[i].polygon.setMap(null);
            }
        }
    }
    else{
        for (var i = 0; i < this.regionSchedules.length; i++){
            if (this.regionSchedules[i].isActive){
                this.regionSchedules[i].marker.setMap(this.map);
                if (this.regionSchedules[i].circle){
                    this.regionSchedules[i].circle.setMap(this.map);
                }
                if (this.regionSchedules[i].polygon){
                    this.regionSchedules[i].polygon.setMap(this.map);
                }
            }
        }
    }

    this.showingRegions = !this.showingRegions;
}

toggleGrants(){
    if (this.showingGrants){
        for (var i = 0; i < this.spectrumGrants.length; i++){
            this.spectrumGrants[i].marker.setMap(null);

            if (this.spectrumGrants[i].circle){
                this.spectrumGrants[i].circle.setMap(null);
            }
            if (this.spectrumGrants[i].polygon){
                this.spectrumGrants[i].polygon.setMap(null);
            }
        }
    }
    else{
        for (var i = 0; i < this.spectrumGrants.length; i++){
            this.spectrumGrants[i].marker.setMap(this.map);
            if (this.spectrumGrants[i].circle){
                this.spectrumGrants[i].circle.setMap(this.map);
            }
            if (this.spectrumGrants[i].polygon){
                this.spectrumGrants[i].polygon.setMap(this.map);
            }
        }
    }

    this.showingGrants = !this.showingGrants;
}

drawShape(regionSchedule: RegionScheduler){
    regionSchedule.isShowing = true;
    //var coordinateArray = regionSchedule.shapePoints.split(',');
    //var coor = new google.maps.LatLng(coordinateArray[0], coordinateArray[1]);


    regionSchedule.marker.setMap(this.map);

    if (regionSchedule.regionShape == "circle"){
        regionSchedule.circle.setMap(this.map);
        //this.addMarker(coor, regionSchedule.regionName + ' ' + 'Radius: ' + regionSchedule.shapeRadius);
    }
    else if (regionSchedule.regionShape == "polygon"){
        regionSchedule.polygon.setMap(this.map);
    }
    else {
        console.log('shapeError');
    }
}
removeShape(regionSchedule: RegionScheduler){
    regionSchedule.isShowing = false;

    regionSchedule.marker.setMap(null);
    if (regionSchedule.regionShape == "circle"){
        regionSchedule.circle.setMap(null);
    }
    else if (regionSchedule.regionShape == 'polygon'){
        regionSchedule.polygon.setMap(null);
    }
    else {
        console.log('shapeError');
    }

}




private latLongToShapePoints(latLong: Coordinates): String {
    var latLongString = "";
    latLongString = latLong.toString();
    latLongString = latLongString.replace(' ', '');
    latLongString = latLongString.replace('(', '');
    latLongString = latLongString.replace(')', '');
    return latLongString;
}


@ViewChild('mapContainer', {static: false}) gmap: ElementRef;

// ~ Fields ........................................................
// -----------------------------------------------------------------
private map: google.maps.Map;
private infoWindow: google.maps.InfoWindow = new google.maps.InfoWindow;

// Array of the Circle objects that exist for this map
//private circles: google.maps.Circle[] = [];

// Array of the Marker objects that exist for this map
//private markers: google.maps.Marker[] = [];

// Coordinate object that will be used below in API functions
// By default, Virginia Tech's coordinates are used
private coordinates = new google.maps.LatLng(37.2296, -80.4179);

// private coordinates = new google.maps.LatLng(37.2314, -80.4221);
// Specifies certain map features, such as center, zoom, map type, etc.
private mapOptions: google.maps.MapOptions = {
    center: this.coordinates,
    zoom: 13,
    // zoom: 19.5,
    mapTypeId: 'terrain'
};


// ~ Methods .......................................................
// -----------------------------------------------------------------
    /**
     * This method will be called immediately after ViewInit
     */
     ngAfterViewInit() {
         this.mapInitializer();
     }

    /**
     * Initializes the map, setting it to the user's GPS coordinates,
     * or the default coordinate of Virginia Tech if Geolocation is not
     * supported or permitted by the user
     */
     mapInitializer() {
         // Set the Map to the default coordinates, Virginia Tech
         this.map = new google.maps.Map(this.gmap.nativeElement, this.mapOptions);
         // (This is was converted to TS from JS code provided by Google)
         // Source: https://developers.google.com/maps/documentation/javascript/geolocation
         if (navigator.geolocation) {
             navigator.geolocation.getCurrentPosition(position => {

                 // Create a gpsPosition variable to hold these two coordinates
                 const gpsPosition = {
                     lat: position.coords.latitude,
                     lng: position.coords.longitude
                 };

                 // Set the new coordinates
                 this.coordinates = new google.maps.LatLng(gpsPosition.lat, gpsPosition.lng);

                 this.infoWindow.setPosition(gpsPosition);
                 this.infoWindow.setContent('Location found.');
                 this.infoWindow.open(this.map);
                 this.map.setCenter(gpsPosition);

                 // Add a Marker to confirm that the method addMarker works
                 // Add a Circle to confirm that the method addCircle works
                 //this.addCircle(this.coordinates, 100);

             }, () => {
                 // Browser supports Geolocation, but something went wrong
                 this.handleLocationError(
                     true, this.infoWindow, this.map.getCenter());
             });
         }
         else {
             // Browser doesn't support Geolocation
             this.handleLocationError(
                 false, this.infoWindow, this.map.getCenter());
         }
     }

    /**
     * Handles any location errors
     *
     * @param browserHasGeolocation
     *              Boolean value representing if the browser supports geolocation
     * @param infoWindow
     *              The InfoWindow object to display any error messages to
     * @param position
     *              The position on the map to set infoWindow at
     */
     handleLocationError(
         browserHasGeolocation: Boolean,
         infoWindow: google.maps.InfoWindow,
         position) {

         this.infoWindow.setPosition(position);
         this.infoWindow.setContent(browserHasGeolocation ?
             'Error: The Geolocation service failed.' :
             'Error: Your browser doesn\'t support geolocation.');
         this.infoWindow.open(this.map);
     }



 }


