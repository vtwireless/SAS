import { Injectable } from '@angular/core';
export interface Logger {
  error(msg: string);
  debug(msg: string);
}

export const Level = {
  DEBUG: 0,
  ERROR: 5
};

// TODO Create a CloudWatchLoggerService or RollbarLoggerService
@Injectable({
  providedIn: 'root'
})
export class LoggerService implements Logger {

  constructor() { }

  public error(...msg: any[]) {
      this.log(Level.ERROR, msg);
  }

  public debug(...msg: any[]) {
      this.log(Level.DEBUG, msg);
  }

  private log(level: number, msg: any) {
      let _out;
      if (level === Level.ERROR) {
          _out = console.error.bind(console);
      } else {
          _out = console.log.bind(console);
      }

      if (msg.length === 1 && typeof msg[0] === 'string') {
          _out(msg[0]);
      } else if (typeof msg[0] === 'string') {
          const msg0 = msg.shift();
          if (msg.length === 1) {
              msg = msg[0];
          }
          _out(msg0, msg);
      } else {
          if (msg.length === 1) {
              msg = msg[0];
          }
          _out(msg);
      }
  }

}
