from OpenSSL import crypto
import os
import sys
import datetime

# Variables
TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA

now = datetime.datetime.now()
d = now.date()

# Pull these out of scope
cn = 'mdsas'
key = crypto.PKey()
keypath = "certs/" + cn + '-' + str(d) + '.key'
csrpath = "certs/" + cn + '-' + str(d) + '.csr'
crtpath = "certs/" + cn + '-' + str(d) + '.crt'


# Generate the key
def generatekey():
    if os.path.exists(keypath):
        print("Certificate file exists, aborting.")
        print(keypath)
        sys.exit(1)
    # Else write the key to the keyfile
    else:
        print("Generating Key Please standby")
        key.generate_key(TYPE_RSA, 4096)
        with open(keypath, "w") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    # return key


# Generate CSR
def generatecsr():
    print("How would you like to generate csr data?\n"
          "1) VirginiaTech (For Self-Signed Certs).\n"
          "2) Specify your own.")

    option = input("Choose (1/2): ")
    if option == 1:
        c = 'US'
        st = 'Virginia'
        l = 'Blacksburg'
        o = 'VirginiaTech'
        ou = 'Wireless@VT'
    elif option == 2:
        c = input('Enter your country(ex. US): ')
        st = input("Enter your state(ex. Nevada): ")
        l = input("Enter your location(City): ")
        o = input("Enter your organization: ")
        ou = input("Enter your organizational unit(ex. IT): ")
    else:
        print("Incorrect Input provided. Exiting")
        sys.exit(1)

    req = crypto.X509Req()
    req.get_subject().CN = cn
    req.get_subject().C = c
    req.get_subject().ST = st
    req.get_subject().L = l
    req.get_subject().O = o
    req.get_subject().OU = ou
    req.set_pubkey(key)
    req.sign(key, "sha256")

    if os.path.exists(csrpath):
        print("Certificate File Exists, aborting.")
        print(csrpath)
    else:
        with open(csrpath, "w") as f:
            f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, req))
        print("Success")

    # Generate the certificate
    reply = str(input('Is this a Self-Signed Cert (y/n): ')).lower().strip()

    if reply[0] == 'y':
        cert = crypto.X509()
        cert.get_subject().CN = cn
        cert.get_subject().C = c
        cert.get_subject().ST = st
        cert.get_subject().L = l
        cert.get_subject().O = o
        cert.get_subject().OU = ou
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(315360000)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, "sha256")

        if os.path.exists(crtpath):
            print("Certificate File Exists, aborting.")
            print(crtpath)
        else:
            with open(crtpath, "w") as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            print("CRT Stored Here :" + crtpath)


generatekey()
generatecsr()

print("Key Stored Here :" + keypath)
print("CSR Stored Here :" + csrpath)
