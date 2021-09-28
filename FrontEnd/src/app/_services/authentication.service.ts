import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { User, AppConstants } from '../_models/models';
import { HttpRequestsService } from './http-requests.service';


@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
   private currentUserSubject: BehaviorSubject<User>;
    public currentUser: Observable<User>;
    POSTAPI = AppConstants.POSTURL;

    constructor(private httpRequests: HttpRequestsService) {
        this.currentUserSubject = new BehaviorSubject<User>(JSON.parse(localStorage.getItem('currentUser')));
        this.currentUser = this.currentUserSubject.asObservable();
    }

    public get currentUserValue(): User {
        return this.currentUserSubject.value;
    }

    suLogin(model : {username: string, password: string}): Observable<any> {
      console.log("Inside auth");  
      return this.httpRequests.suLogin(model);
    }

    adminLogin(model : {username: string, password: string}): Observable<any> {
      return this.httpRequests.adminLogin(model);
    }
    
    logout() {
        // remove user from local storage to log user out
        localStorage.removeItem('currentUser');
        this.currentUserSubject.next(null);
    }
}
/**]
 * 

import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { AuthenticationDetails, CognitoUser, CognitoUserAttribute } from 'amazon-cognito-identity-js';
import { Observer } from 'rxjs/Observer';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { JwtHelper } from 'angular2-jwt';
import 'rxjs/add/observable/of';
import 'rxjs/add/operator/map';

import { CognitoService } from './cognito.service';
import { LoggerService } from './logger.service';

export interface SignInCallbacks {
  onSignedIn();
  onFirstSignIn();
  onCreateNewPasswordFailed(error);
  onAuthenticationFailed(error);
  onUserAgreement();
  onSignOut();
}

export interface ChangePasswordCallbacks {
  onChangePasswordFailed(error);
  onPasswordChanged();
}

export interface ResetPasswordCallbacks {
  onVerificationCodeSuccess(data);
  onVerificationCodeFailed(error);
  onConfirmPasswordFailed(error);
  onConfirmPasswordSuccess();
}

@Injectable()
export class AuthenticationService {
  cognitoUser: CognitoUser;
  isAuthenticated = false;
  isAuthenticated$ = new BehaviorSubject<boolean>(true);
  private jwtHelper = new JwtHelper();

  constructor(private cognitoService: CognitoService, private logger: LoggerService) {
    this.hasValidSession().subscribe(result => {
      if (result) {
        this.cognitoService.clearCognitoCredentials();
        this.userHasAgreed(result => {
          this.setIsAuthenticated(result);
        });
      } else {
        this.setIsAuthenticated(false);
      }
    });
  }

  setIsAuthenticated(isAuthenticated: boolean) {
    this.isAuthenticated = isAuthenticated;
    this.isAuthenticated$.next(isAuthenticated);
  }

  hasValidUser(): Observable<CognitoUser> {
    return Observable.create((observer: Observer<CognitoUser>) => {
      let user = this.cognitoService.getCurrentUser();
      if (!user) {
        observer.next(null);
      } else {
        user.getSession(function (err, session) {
          if (err) {
            observer.next(null);
          } else {
            if (session && session.isValid()) {
              observer.next(user);
            } else {
              observer.next(null);
            }
          }
        });
      }
    });
  }

  hasValidSession(): Observable<boolean> {
    return Observable.create((observer: Observer<boolean>) => {
      let user = this.cognitoService.getCurrentUser();
      if (!user) {
        observer.next(false);
      } else {
        user.getSession(function (err, session) {
          if (err) {
            observer.next(false);
          } else {
            observer.next(session && session.isValid());
          }
        });
      }
    });
  }

  getIdToken(): Observable<string> {
    return this.cognitoService.getIdToken();
  }

  authenticate(username: string, password: string, callbacks: SignInCallbacks) {
    const authenticationDetails = new AuthenticationDetails({
      Username: username,
      Password: password
    });

    const userData = {
      Username: username,
      Pool: this.cognitoService.getUserPool()
    };

    const cognitoUser = new CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: (session) => {
        this.cognitoService.clearCognitoCredentials();
        if (session && session.isValid()) {
          this.getDecodedToken().subscribe(token => {
            console.log(token);
            // if (token['custom:web'] !== "true") {
            //   callbacks.onAuthenticationFailed({ message: 'You do not have access to GlobalFlyte Web' });
            // } else {
            this.userHasAgreed((result, err) => {
              if (result) {
                this.setIsAuthenticated(true);
                callbacks.onSignedIn();
              } else {
                if (err) {
                  callbacks.onSignOut();
                } else {
                  callbacks.onUserAgreement();
                }
              }
            });
            // }

          });
        }
      },
      onFailure: (err: any) => callbacks.onAuthenticationFailed(err),
      newPasswordRequired: (userAttributes: any, requiredAttributes: any) => callbacks.onFirstSignIn()
    });
  }


  userHasAgreed(callback: any) {
    callback(true);
    // TODO
    // let user = this.cognitoService.getCurrentUser();
    // if (user) {
    //   user.getSession((err, session) => {
    //     if (session && session.isValid()) {
    //       user.getUserAttributes((err, result) => {
    //         if (!err && result) {
    //           let agreed = false;
    //           for (let attr of result) {
    //             if (attr.getName() == "custom:license_agreement") {
    //               if (attr.getValue()) {
    //                 agreed = true;
    //               }
    //             }
    //           }
    //           callback(agreed);
    //         } else {
    //           callback(false, err);
    //         }
    //       });
    //     } else {
    //       callback(false);
    //     }

    //   });
    // } else {
    //   console.log('NO USER');
    //   callback(false);
    // }
  }

  agreeToLicense(): Observable<boolean> {
    return Observable.create((observer: Observer<boolean>) => {

      let attributeList = [];
      let attribute = new CognitoUserAttribute({
        Name: 'custom:license_agreement',
        Value: new Date().getTime().toString()
      });
      attributeList.push(attribute);

      let user = this.cognitoService.getCurrentUser();
      if (user) {
        user.getSession((err, session) => {
          if (session && session.isValid()) {
            user.updateAttributes(attributeList, function (err, result) {
              if (err) {
                observer.error(err);
              } else {
                observer.next(true);
              }
            });
          } else {
            observer.next(false);
          }
        });
      } else {
        observer.next(false);
      }
    });
  }

  createNewPassword(username: string, password: string, password2: string, callbacks: SignInCallbacks) {
    const authenticationDetails = new AuthenticationDetails({
      Username: username,
      Password: password
    });

    const userData = {
      Username: username,
      Pool: this.cognitoService.getUserPool()
    };

    const cognitoUser = new CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: () => { },
      onFailure: error => callbacks.onAuthenticationFailed(error),
      newPasswordRequired: (userAttributes, requiredAttributes) => {
        delete userAttributes.email_verified;
        delete userAttributes.phone_number_verified;
        cognitoUser.completeNewPasswordChallenge(password2, userAttributes, {
          onSuccess: (session) => {
            this.userHasAgreed((result, error) => {
              if (result) {
                this.setIsAuthenticated(true);
                callbacks.onSignedIn();
              } else {
                console.log(error);
                if (error) {
                  callbacks.onSignOut();
                } else {
                  callbacks.onUserAgreement();
                }
              }
            });
          },
          onFailure: (err) => callbacks.onCreateNewPasswordFailed(err)
        });
      }
    });
  }

  clearUser() {
    let user = this.cognitoService.getCurrentUser();
    if (user) {
      user.signOut();
    }
  }

  signOut() {
    this.clearUser();
    this.setIsAuthenticated(false);
  }

  // TODO sign out all devices

  changePassword(oldPassword: string, newPassword: string, callbacks: ChangePasswordCallbacks) {
    let cognitoUser = this.cognitoService.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.getSession((err, session) => {
        if (err) {
          callbacks.onChangePasswordFailed('Failed to change password');
        } else {
          cognitoUser.changePassword(oldPassword, newPassword, (err, result) => {
            if (err) {
              callbacks.onChangePasswordFailed(err);
            } else {
              callbacks.onPasswordChanged();
            }
          });
        }
      });
    }
  }

  sendVerificationCode(username: string, callbacks: ResetPasswordCallbacks) {
    const userData = {
      Username: username,
      Pool: this.cognitoService.getUserPool()
    };

    const cognitoUser = new CognitoUser(userData);

    cognitoUser.forgotPassword({
      onSuccess: (result) => callbacks.onVerificationCodeSuccess(result),
      onFailure: (err) => callbacks.onVerificationCodeFailed(err)
    });
  }

  confirmPassword(username: string, verificationCode: string, newPassword: string, callbacks: ResetPasswordCallbacks) {
    const userData = {
      Username: username,
      Pool: this.cognitoService.getUserPool()
    };

    const cognitoUser = new CognitoUser(userData);
    cognitoUser.confirmPassword(verificationCode, newPassword, {
      onSuccess: () => callbacks.onConfirmPasswordSuccess(),
      onFailure: (err: Error) => callbacks.onConfirmPasswordFailed(err)
    });
  }

  getDecodedToken(): Observable<any> {
    return this.cognitoService.getIdToken().map((token) => {
      return this.jwtHelper.decodeToken(token);
    });
  }

}

 */