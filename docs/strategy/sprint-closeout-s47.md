# Sprint Closeout - S47 Hosting and Tenant Architecture

Status: Closed

Audit result: PASS WITH FOLLOW-UPS

## Scope Completed

- `FB-109`: hosting and tenant architecture ADR.
- `FB-110`: production container runtime contract implemented, with local image-build verification still blocked.
- `FB-111`: tenant data boundary and storage model.
- `FB-112`: managed hosting environment baseline.

## Outcome

- Family Book now has an accepted first paid-hosting decision: managed single-tenant family archives.
- Production runtime behavior is explicit and enforced more tightly through `app/runtime_contract.py` plus container startup checks.
- Backup restore now rejects unsafe archive paths instead of trusting `ZipFile.extractall()`.
- Media file and variant path resolution now reject DB-backed traversal outside the archive media root.
- Production and hosted archive env examples now reflect the current SMTP-based auth/invite flow and the new production runtime marker.

## Structural Evidence

- `uv run pytest tests/test_config.py tests/test_runtime_contract.py tests/test_phase3.py -q`
- `uv run pytest tests/test_api.py tests/test_runtime_contract.py tests/test_media.py tests/test_phase3.py -q`
- `bash -n docker/start.sh`
- `git diff --check`

## Documentation Deliverables

- `docs/ops/hosting-and-tenant-architecture-adr.md`
- `docs/ops/hosting-environment-options.md`
- `docs/ops/tenant-data-boundary.md`
- `docs/ops/production-container-runtime.md`
- `docs/ops/managed-hosting-baseline.md`
- `.env.production.example`
- `.env.hosted-archive.example`

## Notes

- `docker build -t family-book:local .` could not be executed in this environment because no local container runtime is installed.
- `FB-110` should remain `Partial` until a real image build is run on a machine with Docker or an equivalent container builder.
- The two untracked `docs/bizanalysis/*` analyst input files remain untouched and are not part of S47 deliverables.
