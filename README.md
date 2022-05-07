# ISCC - Decentralized Content Registry

[![Tests](https://github.com/iscc/iscc-registry/actions/workflows/tests.yml/badge.svg)](https://github.com/iscc/iscc-registry/actions/workflows/tests.yml)

## About `iscc-registry`

`iscc-registry` is a web application for running a decentralized, cross-chain, content
registry (also called Meta-Registry) based on the declaration protocol of the
**International Standard Content Code** ([ISCC](https://iscc.codes)).

## Overview

<img align="left" width="200" src="docs/iscc-id-listing.jpg?raw=true">

**Frontend**

The frontend application installt at the domain root shows a listing of the latest ISCC
registrations and allows for basic search and detail views of declaration data.
URL of the scheme my-install.site/<iscc-id> are resolved to their indended redirection target.
<br clear="left"/>

<img align="left" width="200" src="docs/iscc-registry-api.jpg?raw=true">

**API**

The app also provides a REST API for ISCC-ID lookups and syncronization with observers.
An interactive demo frontend is available at my-install.site/api/v1/docs
<br clear="left"/>

<img align="left" width="200" src="docs/iscc-registry-dashboard.jpg?raw=true">

**Dashboard**

The backend application supports content moderation for operators at my-install.site/dashboard.
<br clear="left"/>

## Background

An ISCC-CODE is an open-source, content-based identifier and fingerprint for digital media assets.
By declaring ISCC-CODEs on public blockchains users can obtain a short and globally unique ISCC-ID
which associates the ISCC-CODE with their blockchain wallet address/identity and optionally a link
to machine-readable external metadata.

![ISCC Decentralized Content Registry Architecture](docs/iscc-decentralized-content-registry.svg)

Public [ISCC-CODE declarations](https://github.com/iscc/iscc-evm) from different blockchains are
monitored by [ISCC-OBSERVERs](https://github.com/iscc/iscc-observer-evm) and registered with an
`iscc-registry` via its REST Api. The `iscc-registry` calculates and indexes ISCC-IDs based on the
events received from observers. The resulting ISCC-IDs are identifiers for digital media assets
with the following mandatory information attached:

- An ISCC-CODE, which is a content-based identifier and fingerprint of a media assset
- A DECLARER, which is the blockchain address of entity that signed a declaration transaction
- A timestamp of the declaration

An ISCC declaraton can optionally provide

- A URL with extended [metdadata](https://schema.iscc.codes) about the digital media asset
- A redirection target that can be used like a URL-shortener (e.g. `https://iscc-reg.tld/<iscc-id>`)
- The blockchain address of a registrar that facilitated the declaration

## Develoment Setup

**Requirements:**

- [Python](https://www.python.org/) 3.8 - 3.10
- [Poetry](https://python-poetry.org/)

Get up and running:
```shell
git clone https://github.com/iscc/iscc-registry.git
cd iscc-registry
poetry install
poe demo
python manage.py runserver
```

## Configuration
The service is configured via environment variables:

- **`DEBUG`** - Run the service in debug mode (True/False). Disable for production use.
- **`TESTNET`** - Enable if you are indexing declarations from testnetworks (True/False).
- **`HUEY_SIMULATE`** - Run background tasks in immediate/blocking mode (True/False). Disable for production use.
- **`SECRET_KEY`** - Set to a unique, unpredictable value (used by Django for cryptographic signing).
- **`OBSERVER_TOKEN`** - Set to a secure string used for authentication of observers.
- **`SITE_ADDRESS`** - Set to domain (including scheme) of the installation.
- **`SITE_EMAIL`** - Set to operators email address (if using Caddyfile).
- **`ALLOWED_HOSTS`** - All domains (without scheme) the web app will respond to.
- **`CSRF_TRUSTED_ORIGINS`** - A comma separated list of trusted origins for unsafe requests (e.g. POST).
- **`CORS_ALLOW_ALL_ORIGINS`** - If True, all origins will be allowed to make api requests.
- **`DATABASE_URL`** - Database url including username password for connecting to database.
- **`POSTGRES_USER`** - Postgres username (if using local postgress containter).
- **`POSTGRES_PASSWORD`** - Postgress password (if using local postrgress container).
- **`REDIS_URL`** - Redis connection string for (used by task queue).
- **`IPFS_GATEWAY`** - IPFS Gateway URL used for ingesting metadata.
- **`IPFS_RETRIES`** - Number of times to try loading metadata via IPFS.
- **`IPFS_RETRY_DELAY`** - Delay between retries in number of seconds.
- **`SENTRY_DSN`** - Optional connection string to sentry.io for error reporting.
- **`READ_TIMEOUT`** - Read timeout in seconds for metadata downloads.

See [example values](.env.dev)
