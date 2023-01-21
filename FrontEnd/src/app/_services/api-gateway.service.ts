/*
import { Injectable } from '@angular/src';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material';
import { Observable } from 'rxjs/Observable';

import { AuthService, MessageService } from '@app/src';

import { environment } from '@env/environment';

const API_URL = environment.apiEndpoint;

@Injectable()
export class ApiGatewayService {

  constructor(private authService: AuthService, private router: Router, private messageService: MessageService,
    public snackBar: MatSnackBar) {
  }

  get<T>(basePath: string, resource: string, options?: any): Observable<T> {
    return this.http.get<T>(`${API_URL}/${basePath}/${resource}`, options)
      .catch((error) => this.handleError(error));
  }

  post<T>(basePath: string, resource: string, body: any, options?: any): Observable<T> {
    return this.http.post<T>(`${API_URL}/${basePath}/${resource}`, body, options)
      .catch((error) => this.handleError(error));
  }

  put(basePath: string, resource: string, body: any, options?: any) {
    return this.http.put(`${API_URL}/${basePath}/${resource}`, body, options)
      .catch((error) => this.handleError(error));
  }

  delete(basePath: string, resource: string, options?: any) {
    return this.http.delete(`${API_URL}/${basePath}/${resource}`, options)
      .catch((error) => this.handleError(error));
  }

  private handleError(error: any) {

    if (error.status === 401) {
      this.authService.signOut();
      this.messageService.disconnect();
      this.router.navigate([environment.signInPath]);
    }

    if (error.status === 403) {
      let errorMessage = (error.error && error.error.errorMessage) ? error.error.errorMessage : 'Access Denied';
      this.snackBar.open(errorMessage, 'OK', {
        duration: 2000,
      });
    }

    if (error.error && error.error.message) {
      return Observable.throw(error.error.message);
    } else {
      return Observable.throw("Unknown error");
    }

  }

}

*/