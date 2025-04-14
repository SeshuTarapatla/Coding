package org.example.certificate;


import org.bouncycastle.asn1.x500.X500Name;
import org.bouncycastle.cert.X509CertificateHolder;
import org.bouncycastle.cert.jcajce.JcaX509CertificateConverter;
import org.bouncycastle.cert.jcajce.JcaX509v3CertificateBuilder;
import org.bouncycastle.operator.ContentSigner;
import org.bouncycastle.operator.jcajce.JcaContentSignerBuilder;
import org.bouncycastle.util.io.pem.PemObject;
import org.bouncycastle.util.io.pem.PemWriter;

import java.io.FileWriter;
import java.io.StringWriter;
import java.math.BigInteger;
import java.security.*;
import java.security.cert.Certificate;
import java.util.Date;

public class X509CertificateGenerator {

    private final String publicKeyData;
    private final String privateKeyData;
    private final String certificateData;


    public X509CertificateGenerator() {
        try {
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
            keyPairGenerator.initialize(2048);

            KeyPair keyPair = keyPairGenerator.generateKeyPair();
            PublicKey publicKey = keyPair.getPublic();
            PrivateKey privateKey = keyPair.getPrivate();
            Certificate certificate = generateCertificate(publicKey, privateKey);

//            saveToPemFile("public-key.pem","PUBLIC KEY", publicKey.getEncoded());
//            saveToPemFile("private-key.pem","PRIVATE KEY", privateKey.getEncoded());
//            saveToPemFile("certificate.pem","CERTIFICATE", certificate.getEncoded());

            publicKeyData = parseToPemFormat("PUBLIC KEY", publicKey.getEncoded());
            privateKeyData = parseToPemFormat("PRIVATE KEY", privateKey.getEncoded());
            certificateData = parseToPemFormat("CERTIFICATE", certificate.getEncoded());
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private Certificate generateCertificate(PublicKey publicKey, PrivateKey privateKey) {
        try {
            int validityInYears = 2;
            long now = System.currentTimeMillis();
            Date startDate = new Date(now);
            Date endDate = new Date(now + validityInYears * 365L * 24 * 60 * 60 * 1000);

            X500Name dnName = new X500Name("CN=Test Certificate");
            BigInteger serial = new BigInteger(64, new SecureRandom());
            JcaX509v3CertificateBuilder certificateBuilder = new JcaX509v3CertificateBuilder(dnName, serial, startDate, endDate, dnName, publicKey);
            ContentSigner contentSigner = new JcaContentSignerBuilder("SHA256WithRSA").build(privateKey);
            X509CertificateHolder certificateHolder = certificateBuilder.build(contentSigner);
            return new JcaX509CertificateConverter().getCertificate(certificateHolder);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private void saveToPemFile(String fileName, String header, byte[] contents) {
        PemObject pemObject = new PemObject(header, contents);
        try (PemWriter pemWriter = new PemWriter(new FileWriter(fileName))) {
            pemWriter.writeObject(pemObject);
            System.out.println(header + " generated successfully and saved to: " + fileName);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private String parseToPemFormat(String header, byte[] contents) {
        PemObject pemObject = new PemObject(header, contents);
        StringWriter stringWriter = new StringWriter();
        try (PemWriter pemWriter = new PemWriter(stringWriter)) {
            pemWriter.writeObject(pemObject);
            pemWriter.flush();
            return stringWriter.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    // Getters
    public String getPublicKey() {
        return publicKeyData;
    }

    public String getPrivateKey() {
        return  privateKeyData;
    }

    public String getCertificate() {
        return certificateData;
    }
}