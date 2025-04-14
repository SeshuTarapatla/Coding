package org.example;

import org.example.certificate.X509CertificateGenerator;

public class Main {
    public static void main(String[] args) {
        System.out.println("Hello world!");
        X509CertificateGenerator certificateGenerator = new X509CertificateGenerator();
        System.out.println("Public Key:\n"+certificateGenerator.getPublicKey());
        System.out.println("Private Key:\n"+certificateGenerator.getPrivateKey());
        System.out.println("Certificate:\n"+certificateGenerator.getCertificate());
    }
}