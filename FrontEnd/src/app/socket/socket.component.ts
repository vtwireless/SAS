import { Component, OnDestroy } from '@angular/core';
import { User } from '../_models/models';
import { Subscription } from 'rxjs';
import { OnInit } from '@angular/core';
import { SocketService, WatchRadio } from '../_services/socket.service';


@Component({
  selector: 'app-socket',
  templateUrl: './socket.component.html',
})
export class SocketComponent { //implements OnInit, OnDestroy{
    title = 'socket-io-example';
    loggedIn = false;
    name: string = "";
    type: string= "";
    user: User;
    watchRadio: WatchRadio;

    socketText: string = "Test";

    constructor(private webSocketService: SocketService) {}

   ngOnInit() {

    }

    ngOnDestroy() {
      this.webSocketService.close();
    }

    startSocket(){
        this.webSocketService.configure("localhost","8000");
        this.webSocketService.listen('connection').subscribe((data) => {
        this.socketText = data.toString();

      })

      this.webSocketService.listen("radioOutput").subscribe((data) => {
        this.socketText = data.toString() + "dB";
      })

       this.watchRadio = new WatchRadio();
       this.watchRadio.radioId = "12345";
       this.webSocketService.emit("watchRadio", this.watchRadio);
    }

    closeSocket(){
      this.webSocketService.close();
    }



}
