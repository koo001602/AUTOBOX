#!/bin/bash
# AutoBox MQTT TLS Certificate Generation Script
# Usage: ./generate-certs.sh [EC2_IP_OR_DOMAIN]
#
# This script generates self-signed certificates for MQTT TLS communication:
# - CA certificate (ca.crt, ca.key)
# - Server certificate (server.crt, server.key)
# - Client certificate for Raspberry Pi (client.crt, client.key)

set -e

# Configuration
CERT_DIR="$(dirname "$0")"
DAYS_VALID=365
KEY_SIZE=2048

# Get EC2 IP or domain from argument or use default
EC2_HOST="${1:-localhost}"

echo "========================================"
echo "AutoBox MQTT TLS Certificate Generator"
echo "========================================"
echo "EC2 Host: $EC2_HOST"
echo "Output Directory: $CERT_DIR"
echo "Validity: $DAYS_VALID days"
echo ""

cd "$CERT_DIR"

# 1. Generate CA (Certificate Authority)
echo "[1/3] Generating CA certificate..."
openssl genrsa -out ca.key $KEY_SIZE

openssl req -new -x509 -days $DAYS_VALID -key ca.key -out ca.crt -subj "/C=KR/ST=Seoul/L=Seoul/O=AutoBox/OU=IoT/CN=AutoBox-CA"

echo "  - ca.key (private key)"
echo "  - ca.crt (certificate)"

# 2. Generate Server Certificate
echo ""
echo "[2/3] Generating server certificate..."

# Create server config for SAN (Subject Alternative Name)
cat > server.cnf << EOF
[req]
default_bits = $KEY_SIZE
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
C = KR
ST = Seoul
L = Seoul
O = AutoBox
OU = IoT
CN = $EC2_HOST

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = mosquitto
DNS.3 = $EC2_HOST
IP.1 = 127.0.0.1
EOF

# Add EC2 IP if it looks like an IP address
if [[ $EC2_HOST =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "IP.2 = $EC2_HOST" >> server.cnf
fi

openssl genrsa -out server.key $KEY_SIZE

openssl req -new -key server.key -out server.csr -config server.cnf

openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days $DAYS_VALID -extensions req_ext -extfile server.cnf

echo "  - server.key (private key)"
echo "  - server.crt (certificate)"

# 3. Generate Client Certificate (for Raspberry Pi)
echo ""
echo "[3/3] Generating client certificate..."

openssl genrsa -out client.key $KEY_SIZE

openssl req -new -key client.key -out client.csr \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=AutoBox/OU=IoT/CN=raspberry-pi"

openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out client.crt -days $DAYS_VALID

echo "  - client.key (private key)"
echo "  - client.crt (certificate)"

# Cleanup temporary files
rm -f server.csr client.csr server.cnf ca.srl

# Set permissions
chmod 644 ca.crt server.crt client.crt
chmod 600 ca.key server.key client.key

echo ""
echo "========================================"
echo "Certificate generation complete!"
echo "========================================"
echo ""
echo "Files generated:"
echo "  CA:     ca.crt, ca.key"
echo "  Server: server.crt, server.key"
echo "  Client: client.crt, client.key"
echo ""
echo "Next steps:"
echo "  1. Copy ca.crt and client.* to Raspberry Pi"
echo "  2. Configure Mosquitto to use server.crt and server.key"
echo "  3. Restart Docker containers: docker-compose up -d"
echo ""
