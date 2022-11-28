import { Injectable } from '@angular/core';
import { io } from 'socket.io-client';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class SocketService {

    socket: any;
    uri = '';
    private port = '';

    constructor() {}

    configure(uri: string, port: string) {
        this.uri = uri;
        this.port = port;
        this.socket = io(this.uri + ':' + this.port);
    }

    listen(eventName: string) {
        return new Observable((subscriber) => {
            this.socket.on(eventName, (data) => {
                subscriber.next(data);
            });
        });
    }

    emit(eventName: string, data: any) {
        this.socket.emit(eventName, data);
    }

    close() {
        this.socket.close();
    }
}

export class WatchRadio {
    public radioId: string;
}
