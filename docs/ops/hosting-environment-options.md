# Hosting Environment Options

## Goal

Record the practical hosting options for the current Family Book runtime shape: one SQLite database plus one `DATA_DIR` tree for media, variants, backups, and exports.

## Current Runtime Constraint

The app expects persistent filesystem state. That means the first hosted environment must provide durable storage to the app runtime.

## Option Summary

| Option | Fit For Current App | Notes |
|---|---|---|
| Railway single service plus volume | Good | Already close to the current release flow. |
| Render web service plus persistent disk | Good | Similar single-archive shape if disk is mounted to the app. |
| AWS ECS/Fargate plus EFS | Good | Strong managed option for isolated single-archive tasks. |
| EC2 or Lightsail single host | Good | Operationally simple but more hands-on. |
| App Runner-style stateless service | Poor for now | Current app expects durable filesystem state. |
| Pooled multi-tenant SaaS runtime | Poor for now | Requires tenant redesign, not just hosting setup. |

## Railway

Why it fits:

- single runtime per archive is straightforward
- persistent volume can hold SQLite and media
- current release flow already assumes `/data`

Watchouts:

- treat staging and production volumes as separate archives
- keep restore and backup procedures outside ad hoc operator memory
- avoid using one service instance for multiple paying archives

Reference:

- [Railway volumes guide](https://docs.railway.com/guides/volumes)

## Render

Why it fits:

- similar single-service deployment model
- persistent disk can mount the archive state

Watchouts:

- disk mount path must align with `DATA_DIR`
- SQLite and media still need archive-level isolation

Reference:

- [Render persistent disks](https://render.com/docs/disks)

## AWS ECS/Fargate Plus EFS

Why it fits:

- container scheduling stays managed
- EFS can provide the persistent archive filesystem expected by the app
- clearer path to one service or task set per archive

Watchouts:

- EFS cost and latency must be acceptable for SQLite workload patterns
- backup and restore still need operator runbooks

Reference:

- [Amazon ECS EFS volumes](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/efs-volumes.html)

## EC2 Or Lightsail Single Host

Why it fits:

- closest to the app's current assumptions
- easiest mental model for one family archive per machine or per mounted data volume

Watchouts:

- patching, backups, and monitoring are more operator-heavy
- scaling is manual

## Why App Runner Is Not The First Choice

This is an inference from Family Book's current architecture, not a blanket statement about the platform.

Family Book currently assumes:

- durable local filesystem state
- one SQLite file
- one media and backup tree

Until the app moves durable state to services such as managed SQL plus object storage, a stateless container platform is the wrong default fit.
