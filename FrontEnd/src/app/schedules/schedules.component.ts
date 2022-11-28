import { Component, AfterViewInit, ViewChild, ElementRef, Inject } from '@angular/core';
import { PrimaryUser, SecondaryUser, RegionScheduler, User, AppConstants, MapColorConstants } from '../_models/models';
import { Router, ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { HttpRequestsService } from '../_services/http-requests.service';

@Component({
  selector: 'app-schedules',
  templateUrl: './schedules.component.html'
})
export class SchedulesComponent implements AfterViewInit{

  regionSchedules: Array<RegionScheduler> = [];
  model = new RegionScheduler(null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, []);
  radiusArray = [25, 50, 100, 250, 500, 1000, 5000, 10000];
  shapeArray = ["circle", "polygon"];
  showIndividual = false;
  tierID = '';
  GETAPI = AppConstants.GETURL;
  POSTAPI = AppConstants.POSTURL;
  deleting = false;
  MEGA = 1000000;
  GIGA = 1000000000;
  showingAll = false;
  addingRS = false;
  updatingRS = false;
  schedulingAlgorithmArray = ["FIFO", "SJN", "Test 1", "Test 2"];


  constructor(private httpRequests: HttpRequestsService, private route: ActivatedRoute, @Inject('BASE_URL') baseUrl: string, router: Router) {

    if(localStorage.getItem('currentUser')){
      let user = new User('', '', '');
      user = JSON.parse(localStorage.getItem('currentUser'));
      if(user.userType != 'ADMIN'){
        router.navigate(['/']);
      }
      else{

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
                map: null,
                center: coor,
                radius: this.regionSchedules[i].shapeRadius
              });
              var markerLabel = this.regionSchedules[i].regionName + ", Radius:" + this.regionSchedules[i].shapeRadius + 'm';
              var marker = new google.maps.Marker({
                position: coor,
                map: null,
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
                map: null,
                label: markerLabel
              });
              this.regionSchedules[i].marker = marker;

              this.regionSchedules[i].polygon = new google.maps.Polygon({
                strokeColor: MapColorConstants.regionColor,
                strokeOpacity: MapColorConstants.strokeOpacity,
                strokeWeight: MapColorConstants.strokeWeight,
                fillColor: MapColorConstants.regionColor,
                fillOpacity: MapColorConstants.fillOpacity,
                map: null,
                paths: this.regionSchedules[i].polygonCoordinates
              });
            }
            else {
              console.log('shape error');
            }
          }
      }
        }, error => console.error(error));

      }
    }
  }
  toggleDeleting(){
    this.deleting = !this.deleting;
  }




  createRegionAssignment(){
      /*let params = new HttpParams();
      params = params.set("action",  "alterTierClassAssignment");
      params = params.set("secondaryUserID",  this.model.secondaryUserID);
      params = params.set("tierClassID", this.tierID);
      params = params.set("innerTierLevel", this.model.innerTierLevel.toString());
      params = params.set("isNewTA", true.toString());

      this.http.post(this.POSTAPI, params).subscribe(data => {
         if(data['status'] == '1'){

            /*for(var i = 0; i < this.SecondaryUsers.length; i++){
              if (this.SecondaryUsers[i].tierAssignmentID == secondaryUser.tierAssignmentID){
                this.SecondaryUsers.splice(i, 1);
                i--;
              }
            }*//*
         }


       }, error => console.error(error));*/
     }



     updateRegionSchedule(){
       if (this.model.polygon != null){
         this.updatePolygonCoords();
        }
        this.httpRequests.updateRegionSchedule(this.model).subscribe(data => {
         if(data['status'] == '1'){
           this.updatingRS = false;
           this.model.isEditing = false;
         }
         else{
           console.log("error occurred while updating");
         }


       }, error => console.error(error));
     }
     createRegionSchedule(){
       if (this.model.polygon != null){
         this.updatePolygonCoords();
       }
       this.httpRequests.createRegionSchedule(this.model).subscribe(data => {
         if(data['status'] == '1'){
           this.model.regionID = data['regionID'];
           
           this.model.isEditing = false;
           this.addingRS = false;
           this.regionSchedules.push(this.model);
           
         }
         else{
           console.log("error occurred while creating");
         }


       }, error => console.error(error));
     }


     showAll(){
       var i = 0;
       this.showingAll = true;
       for (i = 0; i < this.regionSchedules.length; i++){
         this.regionSchedules[i].isShowing = true;
         this.drawShape(this.regionSchedules[i]);
       }
     }

     hideAll(){
       this.showingAll = false;
       var i = 0;
       for (i = 0; i < this.regionSchedules.length; i++){
         this.regionSchedules[i].isShowing = false;
         this.removeShape(this.regionSchedules[i]);
       }
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
       this.showingAll = false;

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

     addRS(){
       this.addingRS = true;
       this.model = new RegionScheduler(null, null, "circle", 500, null, null, null, null, null, null, null, null, true, null, null, null, []);
       this.updatingRS = false;
       var markerLabel = "New Region, Radius:" + this.model.shapeRadius + 'm';
              this.model.marker = new google.maps.Marker({
                position: this.map.getCenter(),
                map: this.map,
                //title: message,
                label: markerLabel
              });
       this.model.marker.setDraggable(true);
       var regionSchedule = this.model;
       var latLongString = "";
       latLongString = this.map.getCenter().toString();
       latLongString = latLongString.replace(' ', '');
       latLongString = latLongString.replace('(', '');
       latLongString = latLongString.replace(')', '');
       this.model.shapePoints = latLongString;
       this.model.marker.addListener('dragend', function() {
         //map.setZoom(8);
         var latLongString = "";
         latLongString = this.getPosition().toString();
         latLongString = latLongString.replace(' ', '');
         latLongString = latLongString.replace('(', '');
         latLongString = latLongString.replace(')', '');
         regionSchedule.shapePoints = latLongString;
         regionSchedule.circle.setCenter(regionSchedule.marker.getPosition());

       });

       this.model.circle =  new google.maps.Circle({
         strokeColor: MapColorConstants.regionColor,
         strokeOpacity: MapColorConstants.strokeOpacity,
         strokeWeight: MapColorConstants.strokeWeight,
         fillColor: MapColorConstants.regionColor,
         fillOpacity: MapColorConstants.fillOpacity,
         map: this.map,
         center: this.map.getCenter(),
         radius: this.model.shapeRadius
       });

     }
     cancelAddRS() {
       if (this.model.polygon){
       this.model.polygon.setMap(null);
       }
       if (this.model.marker){
       this.model.marker.setMap(null);
     }
     if (this.model.circle){
       this.model.circle.setMap(null);
     }
       this.model = new RegionScheduler(null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, []);
       this.addingRS = false;
       this.updatingRS = false;
       var i = 0;
       for (i = 0; i < this.regionSchedules.length; i++){
         this.regionSchedules[i].isEditing = false;
         this.regionSchedules[i].marker.setDraggable(false);
         this.regionSchedules[i].marker.addListener('click', null);
         if (this.model.regionShape == "polygon"){
           this.regionSchedules[i].polygon.setEditable(false);
           this.regionSchedules[i].polygon.setDraggable(false);
           this.regionSchedules[i].polygon.addListener('dragend', null);
           this.regionSchedules[i].polygon.addListener('insert_at', null);
           this.regionSchedules[i].polygon.addListener('set_at', null);
         }

         
       }

     }

     editRS(regionSchedule: RegionScheduler) {
       //this.addingRS = true;
       this.updatingRS = true;
       this.model = regionSchedule; 
       this.model.isEditing = true;
       if (regionSchedule.regionShape == "circle"){
         this.model.marker.setDraggable(true);
         regionSchedule.marker.addListener('dragend', function() {
           //map.setZoom(8);
           var latLongString = "";
           latLongString = regionSchedule.marker.getPosition().toString();
           latLongString = latLongString.replace(' ', '');
           latLongString = latLongString.replace('(', '');
           latLongString = latLongString.replace(')', '');
           regionSchedule.shapePoints = latLongString;
           regionSchedule.circle.setCenter(regionSchedule.marker.getPosition());

         });

       }
       else if (regionSchedule.regionShape == "polygon"){
         regionSchedule.polygon.setEditable(true);
         regionSchedule.polygon.setDraggable(true);
         regionSchedule.marker.setMap(null);
         //regionSchedule.polygon.addListener('dragend', this.updatePolygonCoords);
         //regionSchedule.polygon.addListener('insert_at', this.updatePolygonCoords);
         //regionSchedule.polygon.addListener('set_at', this.updatePolygonCoords);


       }
       this.hideAll();
       this.drawShape(this.model);
       this.updatingRS = true;

     }

     updatePolygonCoords(){
       this.model.polygon.setDraggable(false);
       this.model.polygon.setEditable(false);
       this.model.marker.setMap(this.map);

       var len = this.model.polygon.getPath().getLength();
       this.model.shapePoints = this.model.polygon.getPath().getArray()[0].lat()+','
       + this.model.polygon.getPath().getArray()[0].lng();
       var totalLat = this.model.polygon.getPath().getArray()[0].lat();
       var totalLong = this.model.polygon.getPath().getArray()[0].lng();
       for (var k = 1; k < len; k++){
         var xy = this.model.polygon.getPath().getArray()[k];
         this.model.shapePoints = this.model.shapePoints + ',' + xy.lat() + ',' + xy.lng();
         totalLat = totalLat + xy.lat();
         totalLong = totalLong + xy.lng();
       }
       totalLat = totalLat/len;
       totalLong = totalLong/len;
       this.model.marker.setPosition(new google.maps.LatLng(totalLat, totalLong));

       this.model.polygonCoordinates = this.model.polygon.getPath().getArray();
       console.log(this.model.polygon.getPath().getArray());

     }

     private latLongToShapePoints(latLong): String {
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

     // Specifies certain map features, such as center, zoom, map type, etc.
     private mapOptions: google.maps.MapOptions = {
       center: this.coordinates,
       zoom: 13,
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

     updateCircleRadius(){
       this.model.circle.setMap(null);
       this.model.marker.setLabel(this.model.regionName + ", Radius:" + this.model.shapeRadius + 'm');
       this.model.circle.setRadius(Number(this.model.shapeRadius));
       this.model.circle.setMap(this.map);

     }


     removePoint(){
       var len = this.model.polygon.getPath().getArray().length;
       if (this.model.regionShape == "polygon" && len > 3 && len > 1){
         this.model.polygon.getPath().removeAt(len-1);
         this.updatePolygonCoords();
       }
     }

     changeShape(){
       if (this.model.regionShape == "circle"){
         this.model.polygon.setMap(null);
         this.model.polygon = null;
         this.model.shapeRadius = 500;
         this.model.marker.setPosition(this.map.getCenter());
         this.model.marker.setLabel((this.model.regionName|| "New Region") + ", Radius:" + this.model.shapeRadius + 'm');
         this.model.marker.setDraggable(true);
         this.model.circle =  new google.maps.Circle({
           strokeColor: MapColorConstants.regionColor,
           strokeOpacity: MapColorConstants.strokeOpacity,
           strokeWeight: MapColorConstants.strokeWeight,
           fillColor: MapColorConstants.regionColor,
           fillOpacity: MapColorConstants.fillOpacity,
           map: this.map,
           center: this.map.getCenter(),
           radius: this.model.shapeRadius
         })
         this.model.marker.setMap(this.map);
       }
       else if (this.model.regionShape == "polygon"){
         this.model.circle.setMap(null);
         this.model.circle = null;
         var mapCenter = this.map.getCenter();

         this.model.marker.setPosition(this.map.getCenter());
         this.model.marker.setLabel(this.model.regionName);

         var triangleCoordinates = [
         {lat: mapCenter.lat()-0.01, lng: mapCenter.lng()-0.01},
         {lat: mapCenter.lat()+0.01, lng: mapCenter.lng()},
         {lat: mapCenter.lat()+0.01, lng: mapCenter.lng()+0.01}
         ];
         this.model.polygon = new google.maps.Polygon({
           strokeColor: MapColorConstants.regionColor,
           strokeOpacity: MapColorConstants.strokeOpacity,
           strokeWeight: MapColorConstants.strokeWeight,
           fillColor: MapColorConstants.regionColor,
           fillOpacity: MapColorConstants.fillOpacity,
           map: this.map,
           paths: triangleCoordinates
         });
         this.model.polygon.setEditable(true);
         this.model.polygon.setDraggable(true);
       }
       else{
         console.log("shape error");
       }
     }



   }


