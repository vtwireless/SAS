clc; clear;

M = 15; % number of multipaths
N = 100; % number of samples to generate
fd = 1200; % Maximum doppled spread in Hz
Ts = 0.0001; % Sampling period in seconds

a = 0;
b = 2 * pi;
alpha = a + (b-a)*rand(1, M);
beta = a + (b-a)*rand(1, M);
theta = a + (b-a)*rand(1, M);

m = 1:M;
for n = 1:N
    x = cos(((2.*m - 1)*pi + theta)/(4*M));
    h_re(n) = 1/sqrt(M)*sum(cos(2*pi*fd*x*n'*Ts + alpha));
    h_im(n) = 1/sqrt(M)*sum(sin(2*pi*fd*x*n'*Ts + alpha));
end
h = h_re + 1i*h_im;

%{
figure;
subplot(2,1,1);
plot([0:N-1]*Ts, h_re);
title('Real Part');
xlabel('time(s)'); ylabel('Amplitude |hI(t)|');

subplot(2,1,2)
plot([0:N-1]*Ts, h_im);
title('Imaginary Part');
xlabel('time(s)'); ylabel('Amplitude |hI(t)|');
%}

figure;
subplot(2,1,1);
plot([0:N-1]*Ts, 10*log10(abs(h)));
title('Amplitude Response');
xlabel('time(s)'); ylabel('Magnitude |h(t)|');

subplot(2,1,2)
plot([0:N-1]*Ts, angle(h));
title('Phase Response');
xlabel('time(s)'); ylabel('Phase Angle |hI(t)|');

h(1: 6)
yyy = angle(h);
yyy(1: 6)

