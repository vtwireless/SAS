import { Component } from '@angular/core';

@Component({
    selector: 'app-map',
    templateUrl: './map.component.html',
    styleUrls: ['./map.component.css'],
})
export class MapComponent {
    title = 'Kelly Hall Map';
    lat = 37.231396;
    lng = -80.422435;
    lat1 = 37.231666;
    lng1 = -80.422595;
    lat2 = 37.231641;
    lng2 = -80.422565;
    lat3 = 37.231621;
    lng3 = -80.422545;
    lat4 = 37.231605;
    lng4 = -80.422530;
    lat5 = 37.231525;
    lng5 = -80.422450;
    lat6 = 37.231470;
    lng6 = -80.422385;
    lat7 = 37.231410;
    lng7 = -80.422355;
    lat8 = 37.231400;
    lng8 = -80.422345;
    lat9 = 37.231380;
    lng9 = -80.422300;
    lat10 = 37.231320;
    lng10 = -80.422240;
    lat11 = 37.231330;
    lng11 = -80.422190;
    lat12 = 37.231340;
    lng12 = -80.422170;
    lat13 = 37.231315;
    lng13 = -80.422175;
    lat14 = 37.231325;
    lng14 = -80.422150;
    icon = {
        url: '../assets/img/marker.png',
        scaledSize: {
            width: 10,
            height: 15
        }
    };
}

// import { Component, AfterViewInit, ViewChild, ElementRef, Inject } from '@angular/core';
// import { PrimaryUser, SecondaryUser, RegionScheduler, Node, SpectrumGrant, User, PUMap, SUMap, NodeMap, GrantMap, AppConstants, MapColorConstants } from '../_models/models';
// import { Router, ActivatedRoute } from '@angular/router';
// import { Subscription } from 'rxjs';
// import { HttpRequestsService } from '../_services/http-requests.service';
// import { Map, NavigationControl } from 'maplibre-gl';
//
// @Component({
//     selector: 'app-map',
//     templateUrl: './map.component.html',
//     styleUrls: ['./map.component.css']
// })
// export class MapComponent implements AfterViewInit {
//
//     regionSchedules: Array<RegionScheduler> = [];
//     PUs: Array<PUMap> = [];
//     SUs: Array<SUMap> = [];
//     nodes: Array<NodeMap> = [];
//     spectrumGrants: Array<GrantMap> = [];
//
//
//
//
//     showingPUs = true;
//     showingSUs = true;
//     showingNodes = true;
//     showingRegions = true;
//     showingGrants = true;
//
//     GETAPI = AppConstants.GETURL;
//     POSTAPI = AppConstants.POSTURL;
//     MEGA = 1000000;
//     GIGA = 1000000000;
//
//
//
//     constructor(private elementRef: ElementRef, private httpRequests: HttpRequestsService, private route: ActivatedRoute, @Inject('BASE_URL') baseUrl: string, router: Router) {
//
//         if (localStorage.getItem('currentUser')) {
//             let user = new User('', '', '');
//             user = JSON.parse(localStorage.getItem('currentUser'));
//             console.log(user.userType);
//             if (user.userType != 'ADMIN' && user.userType != 'SU') {
//                 router.navigate(['/']);
//             } else {
//                 this.httpRequests.getSecondaryUsers().subscribe(data => {
//                     if (data['status'] == '1') {
//                         for (let j = 0; j < data['secondaryUsers'].length; j++) {
//                             const temp = new SUMap(data['secondaryUsers'][j], null);
//                             this.SUs.push(temp);
//                         }
//                         for (let i = 0 ; i < this.SUs.length; i++) {
//                             this.SUs[i].marker = null;
//                             const coordinateArray = this.SUs[i].secondaryUser.location.split(',');
//                             const coor = new google.maps.LatLng(Number(coordinateArray[0]), Number(coordinateArray[1]));
//                             const markerLabel = this.SUs[i].secondaryUser.secondaryUserName;
//                             const marker = new google.maps.Marker({
//                                 position: coor,
//                                 map: this.map,
//                                 label: markerLabel,
//                                 icon: MapColorConstants.SUIcon
//                             });
//                             this.SUs[i].marker = marker;
//
//                         }
//                     }
//                 }, error => console.error(error));
//                 this.httpRequests.getAllNodes().subscribe(data => {
//                     if (data['status'] == '1') {
//                         for (let j = 0; j < data['nodes'].length; j++) {
//                             const temp = new NodeMap(data['nodes'][j], null, null, null);
//                             this.nodes.push(temp);
//                         }
//                         for (let i = 0 ; i < this.nodes.length; i++) {
//                             this.nodes[i].marker = null;
//                             const coordinateArray = this.nodes[i].node.location.split(',');
//                             const coor = new google.maps.LatLng(Number(coordinateArray[0]), Number(coordinateArray[1]));
//                             const markerLabel = this.nodes[i].node.nodeName;
//                             const marker = new google.maps.Marker({
//                                 position: coor,
//                                 map: this.map,
//                                 label: markerLabel,
//                                 icon: MapColorConstants.NodeIcon
//                             });
//                             this.nodes[i].marker = marker;
//
//                         }
//                     }
//                 }, error => console.error(error));
//                 this.httpRequests.getRegionSchedules().subscribe(data => {
//                     if (data['status'] == '1') {
//                         this.regionSchedules = data['regionSchedules'];
//                         let i = 0;
//                         for (i = 0 ; i < this.regionSchedules.length; i++) {
//                             this.regionSchedules[i].isEditing = false;
//                             this.regionSchedules[i].isShowing = false;
//                             this.regionSchedules[i].marker = null;
//                             const coordinateArray = this.regionSchedules[i].shapePoints.split(',');
//                             const coor = new google.maps.LatLng(Number(coordinateArray[0]), Number(coordinateArray[1]));
//                             if (this.regionSchedules[i].regionShape == 'circle') {
//                                 this.regionSchedules[i].circle =  new google.maps.Circle({
//                                     strokeColor: MapColorConstants.regionColor,
//                                     strokeOpacity: MapColorConstants.strokeOpacity,
//                                     strokeWeight: MapColorConstants.strokeWeight,
//                                     fillColor: MapColorConstants.regionColor,
//                                     fillOpacity: MapColorConstants.fillOpacity,
//                                     map: this.map,
//                                     center: coor,
//                                     radius: this.regionSchedules[i].shapeRadius
//                                 });
//                                 const markerLabel = this.regionSchedules[i].regionName + ', Radius:' + this.regionSchedules[i].shapeRadius + 'm';
//                                 const marker = new google.maps.Marker({
//                                     position: coor,
//                                     map: this.map,
//                                     //title: message,
//                                     label: markerLabel
//                                 });
//                                 this.regionSchedules[i].marker = marker;
//                             } else if (this.regionSchedules[i].regionShape == 'polygon') {
//                                 this.regionSchedules[i].polygonCoordinates = [];
//                                 const coordinatesArray = this.regionSchedules[i].shapePoints.split(',');
//                                 let totalLat = 0;
//                                 let totalLong = 0;
//                                 for (let j = 0; j < coordinateArray.length; j++) {
//                                     this.regionSchedules[i].polygonCoordinates.push(new google.maps.LatLng(Number(coordinatesArray[j]), Number(coordinatesArray[j + 1])));
//                                     totalLat = totalLat + Number(coordinatesArray[j]);
//                                     totalLong = totalLong + Number(coordinatesArray[j + 1]);
//                                     j++;
//                                 }
//                                 totalLat = totalLat / (coordinateArray.length / 2);
//                                 totalLong = totalLong / (coordinateArray.length / 2);
//                                 const markerLabel = this.regionSchedules[i].regionName;
//                                 const marker = new google.maps.Marker({
//                                     position: new google.maps.LatLng(totalLat, totalLong),
//                                     map: this.map,
//                                     label: markerLabel
//                                 });
//                                 this.regionSchedules[i].marker = marker;
//
//                                 this.regionSchedules[i].polygon = new google.maps.Polygon({
//                                     strokeColor: MapColorConstants.regionColor,
//                                     strokeOpacity: MapColorConstants.strokeOpacity,
//                                     strokeWeight: MapColorConstants.strokeWeight,
//                                     fillColor: MapColorConstants.regionColor,
//                                     fillOpacity: MapColorConstants.fillOpacity,
//                                     map: this.map,
//                                     paths: this.regionSchedules[i].polygonCoordinates
//                                 });
//                                 if (!this.regionSchedules[i].isActive) {
//                                     this.regionSchedules[i].marker.setMap(null);
//                                     if (this.regionSchedules[i].polygon) {
//                                         this.regionSchedules[i].polygon.setMap(null);
//                                     }
//                                     if (this.regionSchedules[i].circle) {
//                                         this.regionSchedules[i].circle.setMap(null);
//                                     }
//                                 }
//                             } else {
//                                 console.log('shape error');
//                             }
//                             if (!this.regionSchedules[i].isActive) {
//                                 this.regionSchedules[i].marker.setMap(null);
//                                 if (this.regionSchedules[i].polygon) {
//                                     this.regionSchedules[i].polygon.setMap(null);
//                                 }
//                                 if (this.regionSchedules[i].circle) {
//                                     this.regionSchedules[i].circle.setMap(null);
//                                 }
//                             }
//                         }
//                     }
//                 }, error => console.error(error));
//
//                 this.httpRequests.getSpectrumGrants().subscribe(data => {
//                     if (data['status'] == '1') {
//                         for (let j = 0; j < data['spectrumGrants'].length; j++) {
//                             const temp = new GrantMap(data['spectrumGrants'][j], null, null, null);
//                             this.spectrumGrants.push(temp);
//                         }
//                         for (let i = 0 ; i < this.spectrumGrants.length; i++) {
//                             this.spectrumGrants[i].marker = null;
//                             const coordinateArray = this.spectrumGrants[i].grant.requestLocation.split(',');
//                             const coor = new google.maps.LatLng(Number(coordinateArray[0]), Number(coordinateArray[1]));
//                             const markerLabel = this.spectrumGrants[i].grant.secondaryUserName + ' ' + this.spectrumGrants[i].grant.frequency + 'Hz';
//                             this.spectrumGrants[i].marker = new google.maps.Marker({
//                                 position: coor,
//                                 map: this.map,
//                                 label: markerLabel,
//                                 icon: MapColorConstants.grantIcon
//                             });
//                             this.spectrumGrants[i].circle =  new google.maps.Circle({
//                                     strokeColor: MapColorConstants.grantColor,
//                                     strokeOpacity: MapColorConstants.strokeOpacity,
//                                     strokeWeight: MapColorConstants.strokeWeight,
//                                     fillColor: MapColorConstants.grantColor,
//                                     fillOpacity: MapColorConstants.fillOpacity,
//                                     map: this.map,
//                                     center: coor,
//                                     radius: 500
//                                 });
//
//                         }
//                     }
//                 }, error => console.error(error));
//
// }
// }
// }
//
// togglePUs() {
//     if (this.showingPUs) {
//         for (let i = 0; i < this.PUs.length; i++) {
//             this.PUs[i].marker.setMap(null);
//         }
//     } else {
//         for (let i = 0; i < this.PUs.length; i++) {
//             this.PUs[i].marker.setMap(this.map);
//         }
//     }
//
//     this.showingPUs = !this.showingPUs;
// }
//
// toggleSUs() {
//     if (this.showingSUs) {
//         for (let i = 0; i < this.SUs.length; i++) {
//             this.SUs[i].marker.setMap(null);
//         }
//     } else {
//         for (let i = 0; i < this.SUs.length; i++) {
//             this.SUs[i].marker.setMap(this.map);
//         }
//     }
//
//     this.showingSUs = !this.showingSUs;
// }
// toggleNodes() {
//     if (this.showingNodes) {
//         for (let i = 0; i < this.nodes.length; i++) {
//             this.nodes[i].marker.setMap(null);
//
//             if (this.nodes[i].circle) {
//                 this.nodes[i].circle.setMap(null);
//             }
//             if (this.nodes[i].polygon) {
//                 this.nodes[i].polygon.setMap(null);
//             }
//         }
//     } else {
//         for (let i = 0; i < this.nodes.length; i++) {
//             this.nodes[i].marker.setMap(this.map);
//             if (this.nodes[i].circle) {
//                 this.nodes[i].circle.setMap(this.map);
//             }
//             if (this.nodes[i].polygon) {
//                 this.nodes[i].polygon.setMap(this.map);
//             }
//         }
//     }
//
//     this.showingNodes = !this.showingNodes;
// }
//
// toggleRegions() {
//     if (this.showingRegions) {
//         for (let i = 0; i < this.regionSchedules.length; i++) {
//             this.regionSchedules[i].marker.setMap(null);
//
//             if (this.regionSchedules[i].circle) {
//                 this.regionSchedules[i].circle.setMap(null);
//             }
//             if (this.regionSchedules[i].polygon) {
//                 this.regionSchedules[i].polygon.setMap(null);
//             }
//         }
//     } else {
//         for (let i = 0; i < this.regionSchedules.length; i++) {
//             if (this.regionSchedules[i].isActive) {
//                 this.regionSchedules[i].marker.setMap(this.map);
//                 if (this.regionSchedules[i].circle) {
//                     this.regionSchedules[i].circle.setMap(this.map);
//                 }
//                 if (this.regionSchedules[i].polygon) {
//                     this.regionSchedules[i].polygon.setMap(this.map);
//                 }
//             }
//         }
//     }
//
//     this.showingRegions = !this.showingRegions;
// }
//
// toggleGrants() {
//     if (this.showingGrants) {
//         for (let i = 0; i < this.spectrumGrants.length; i++) {
//             this.spectrumGrants[i].marker.setMap(null);
//
//             if (this.spectrumGrants[i].circle) {
//                 this.spectrumGrants[i].circle.setMap(null);
//             }
//             if (this.spectrumGrants[i].polygon) {
//                 this.spectrumGrants[i].polygon.setMap(null);
//             }
//         }
//     } else {
//         for (let i = 0; i < this.spectrumGrants.length; i++) {
//             this.spectrumGrants[i].marker.setMap(this.map);
//             if (this.spectrumGrants[i].circle) {
//                 this.spectrumGrants[i].circle.setMap(this.map);
//             }
//             if (this.spectrumGrants[i].polygon) {
//                 this.spectrumGrants[i].polygon.setMap(this.map);
//             }
//         }
//     }
//
//     this.showingGrants = !this.showingGrants;
// }
//
// drawShape(regionSchedule: RegionScheduler) {
//     regionSchedule.isShowing = true;
//     //var coordinateArray = regionSchedule.shapePoints.split(',');
//     //var coor = new google.maps.LatLng(coordinateArray[0], coordinateArray[1]);
//
//
//     regionSchedule.marker.setMap(this.map);
//
//     if (regionSchedule.regionShape == 'circle') {
//         regionSchedule.circle.setMap(this.map);
//         //this.addMarker(coor, regionSchedule.regionName + ' ' + 'Radius: ' + regionSchedule.shapeRadius);
//     } else if (regionSchedule.regionShape == 'polygon') {
//         regionSchedule.polygon.setMap(this.map);
//     } else {
//         console.log('shapeError');
//     }
// }
// removeShape(regionSchedule: RegionScheduler) {
//     regionSchedule.isShowing = false;
//
//     regionSchedule.marker.setMap(null);
//     if (regionSchedule.regionShape == 'circle') {
//         regionSchedule.circle.setMap(null);
//     } else if (regionSchedule.regionShape == 'polygon') {
//         regionSchedule.polygon.setMap(null);
//     } else {
//         console.log('shapeError');
//     }
//
// }
//
//
//
//
// private latLongToShapePoints(latLong: Coordinates): String {
//     let latLongString = '';
//     latLongString = latLong.toString();
//     latLongString = latLongString.replace(' ', '');
//     latLongString = latLongString.replace('(', '');
//     latLongString = latLongString.replace(')', '');
//     return latLongString;
// }
//
//
// @ViewChild('mapContainer', {static: false}) gmap: ElementRef;
//
// // ~ Fields ........................................................
// // -----------------------------------------------------------------
// private map: google.maps.Map;
// private infoWindow: google.maps.InfoWindow = new google.maps.InfoWindow;
// private mapBounds = new google.maps.LatLngBounds(
//         new google.maps.LatLng(37.231081, -80.422851),
//         new google.maps.LatLng(37.231712, -80.421992));
// private mapMinZoom = 18;
// private mapMaxZoom = 20;
//
// // Array of the Circle objects that exist for this map
// //private circles: google.maps.Circle[] = [];
//
// // Array of the Marker objects that exist for this map
// //private markers: google.maps.Marker[] = [];
//
// // Coordinate object that will be used below in API functions
// // By default, Virginia Tech's coordinates are used
// private coordinates = new google.maps.LatLng(37.231396, -80.422422);
// private maptiler = new google.maps.ImageMapType({
//         getTileUrl: function(coord, zoom) {
//             const proj = this.map.getProjection();
//             const z2 = Math.pow(2, zoom);
//             const tileXSize = 256 / z2;
//             const tileYSize = 256 / z2;
//             const tileBounds = new google.maps.LatLngBounds(
//                 proj.fromPointToLatLng(new google.maps.Point(coord.x * tileXSize, (coord.y + 1) * tileYSize)),
//                 proj.fromPointToLatLng(new google.maps.Point((coord.x + 1) * tileXSize, coord.y * tileYSize))
//             );
//             const x = coord.x >= 0 ? coord.x : z2 + coord.x;
//             const y = coord.y;
//             if (this.mapBounds.intersects(tileBounds) && (this.mapMinZoom <= zoom) && (zoom <= this.mapMaxZoom)) {
//                 return zoom + '/' + x + '/' + y + '.png';
//             } else {
//                 return '';
//             }
//
//         },
//         tileSize: new google.maps.Size(256, 256),
//     });
// // private coordinates = new google.maps.LatLng(37.2314, -80.4221);
// // Specifies certain map features, such as center, zoom, map type, etc.
// private mapOptions: google.maps.MapOptions = {
//     // mapId: "90f87356969d889c",
//     center: this.coordinates,
//     zoom: 20,
//     // style:`https://maps.googleapis.com/maps/api/js?key=AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg&callback=initMap&v=weekly`,
//
//     // zoom: 19.5,
//     mapTypeId: 'terrain'
// };
//
//
// // ~ Methods .......................................................
// // -----------------------------------------------------------------
//     /**
//      * This method will be called immediately after ViewInit
//      */
//      ngAfterViewInit() {
//         // var s = document.createElement("script");
//         // s.type = "text/javascript";
//         // s.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg&callback=initMap&v=weekly";
//         // this.elementRef.nativeElement.appendChild(s);
//          this.mapInitializer();
//         // this.map.overlayMapTypes.insertAt(0, this.maptiler);
//      }
//
//     /**
//      * Initializes the map, setting it to the user's GPS coordinates,
//      * or the default coordinate of Virginia Tech if Geolocation is not
//      * supported or permitted by the user
//      */
//      mapInitializer() {
//          // Set the Map to the default coordinates, Virginia Tech
//          this.map = new google.maps.Map(this.gmap.nativeElement, this.mapOptions);
//          // this.map.overlayMapTypes.push(this.maptiler);
//          // (This is was converted to TS from JS code provided by Google)
//          // Source: https://developers.google.com/maps/documentation/javascript/geolocation
//          if (navigator.geolocation) {
//              navigator.geolocation.getCurrentPosition(position => {
//
//                  // Create a gpsPosition variable to hold these two coordinates
//                  const gpsPosition = {
//                      lat: position.coords.latitude,
//                      lng: position.coords.longitude
//                  };
//
//                  // Set the new coordinates
//                  this.coordinates = new google.maps.LatLng(gpsPosition.lat, gpsPosition.lng);
//
//                  this.infoWindow.setPosition(gpsPosition);
//                  this.infoWindow.setContent('Location found.');
//                  this.infoWindow.open(this.map);
//                  this.map.setCenter(gpsPosition);
//
//                  // Add a Marker to confirm that the method addMarker works
//                  // Add a Circle to confirm that the method addCircle works
//                  //this.addCircle(this.coordinates, 100);
//
//              }, () => {
//                  // Browser supports Geolocation, but something went wrong
//                  this.handleLocationError(
//                      true, this.infoWindow, this.map.getCenter());
//              });
//          } else {
//              // Browser doesn't support Geolocation
//              this.handleLocationError(
//                  false, this.infoWindow, this.map.getCenter());
//          }
//      }
//
//
//     /**
//      * Handles any location errors
//      *
//      * @param browserHasGeolocation
//      *              Boolean value representing if the browser supports geolocation
//      * @param infoWindow
//      *              The InfoWindow object to display any error messages to
//      * @param position
//      *              The position on the map to set infoWindow at
//      */
//      handleLocationError(
//          browserHasGeolocation: Boolean,
//          infoWindow: google.maps.InfoWindow,
//          position) {
//
//          this.infoWindow.setPosition(position);
//          this.infoWindow.setContent(browserHasGeolocation ?
//              'Error: The Geolocation service failed.' :
//              'Error: Your browser doesn\'t support geolocation.');
//          this.infoWindow.open(this.map);
//      }
//
//
//
//  }
//
//
