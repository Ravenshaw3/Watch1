"""Administrative maintenance routes for Watch1 backend."""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError
from datetime import datetime, timezone
from typing import Any, Callable, Dict

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from maintenance import tasks as maintenance_tasks
from maintenance.tasks import create_job_record, get_job, get_job_history

from .utils import ensure_superuser, handle_permission_error

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")

_MAX_WORKERS = int(os.getenv("WATCH1_ADMIN_WORKERS", "2"))
_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=_MAX_WORKERS)
_job_futures: Dict[int, Future] = {}
_job_results: Dict[int, Dict[str, Any]] = {}
_job_status: Dict[int, str] = {}


@admin_bp.route("/database/jobs/<int:job_id>", methods=["DELETE"])
@jwt_required()
def cancel_job(job_id: int):
    try:
        ensure_superuser()
        future = _job_futures.get(job_id)
        if not future:
            return jsonify({"detail": "Job is not running"}), 404
        if future.cancel():
            _job_status[job_id] = "cancelled"
            _job_results[job_id] = {
                "status": "cancelled",
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            return jsonify({"job_id": job_id, "status": "cancelled"})
        return jsonify({"detail": "Unable to cancel job"}), 409
    except PermissionError as error:
        return handle_permission_error(error)
    except Exception as error:
        print(f"Admin cancel job error: {error}")
        return jsonify({"detail": "Failed to cancel job"}), 500


@admin_bp.route("/worker/health", methods=["GET"])
@jwt_required()
def worker_health():
    try:
        ensure_superuser()
        pending = [job_id for job_id, future in _job_futures.items() if not future.done()]
        return jsonify(
            {
                "max_workers": _MAX_WORKERS,
                "pending_jobs": pending,
                "running": len(pending),
                "completed_result_cache": len(_job_results),
            }
        )
    except PermissionError as error:
        return handle_permission_error(error)
    except Exception as error:
        print(f"Worker health error: {error}")
        return jsonify({"detail": "Failed to fetch worker health"}), 500


@admin_bp.route("/database/info", methods=["GET"])
@jwt_required()
def database_info():
    try:
        ensure_superuser()
        info = maintenance_tasks.get_database_info()
        return jsonify(info)
    except PermissionError as error:
        return handle_permission_error(error)
    except Exception as error:
        print(f"Admin database info error: {error}")
        return jsonify({"detail": "Failed to retrieve database info"}), 500


@admin_bp.route("/database/jobs", methods=["GET"])
@jwt_required()
def job_history():
    try:
        ensure_superuser()
        try:
            limit = int(request.args.get("limit", 20))
        except ValueError:
            return jsonify({"detail": "limit must be an integer"}), 400
        limit = max(1, min(limit, 200))
        jobs = get_job_history(limit=limit)
        for job in jobs:
            result = _job_results.get(job["id"])
            if result is not None:
                job["result"] = result
            status = _job_status.get(job["id"])
            if status is not None:
                job["status"] = status
        return jsonify({"jobs": jobs})
    except PermissionError as error:
        return handle_permission_error(error)
    except Exception as error:
        print(f"Admin jobs error: {error}")
        return jsonify({"detail": "Failed to fetch job history"}), 500


@admin_bp.route("/database/jobs/<int:job_id>", methods=["GET"])
@jwt_required()
def job_status(job_id: int):
    try:
        ensure_superuser()
        job = get_job(job_id)
        if not job:
            return jsonify({"detail": "Job not found"}), 404
        result = _job_results.get(job_id)
        if result is not None:
            job["result"] = result
        status = _job_status.get(job_id)
        if status is not None:
            job["status"] = status
        running = job_id in _job_futures
        job["running"] = running
        return jsonify(job)
    except PermissionError as error:
        return handle_permission_error(error)
    except Exception as error:
        print(f"Admin job status error: {error}")
        return jsonify({"detail": "Failed to fetch job status"}), 500


@admin_bp.route("/database/clean", methods=["POST"])
@jwt_required()
def database_clean():
    return _dispatch_job(
        job_name="db.clean-orphans",
        handler=lambda payload, job_id, started: maintenance_tasks.clean_orphan_media(
            dry_run=not bool(payload.get("apply", False)),
            mark_deleted=not bool(payload.get("delete", False)),
            delete=bool(payload.get("delete", False)),
            job_id=job_id,
            started_at=started,
        ),
    )


@admin_bp.route("/database/prune", methods=["POST"])
@jwt_required()
def database_prune():
    return _dispatch_job(
        job_name="db.prune-test",
        handler=lambda payload, job_id, started: maintenance_tasks.prune_test_media(
            patterns=payload.get("patterns"),
            dry_run=not bool(payload.get("apply", False)),
            delete=bool(payload.get("delete", False)),
            job_id=job_id,
            started_at=started,
        ),
    )


@admin_bp.route("/database/verify-posters", methods=["POST"])
@jwt_required()
def verify_posters():
    return _dispatch_job(
        job_name="db.verify-posters",
        handler=lambda payload, job_id, started: maintenance_tasks.verify_poster_data(
            rebuild_missing=bool(payload.get("rebuild", False)),
            job_id=job_id,
            started_at=started,
        ),
    )


@admin_bp.route("/database/backup", methods=["POST"])
@jwt_required()
def database_backup():
    return _dispatch_job(
        job_name="db.backup",
        handler=lambda payload, job_id, started: maintenance_tasks.backup_database(
            backup_path=payload.get("output"),
            format=payload.get("format", "plain"),
            job_id=job_id,
            started_at=started,
        ),
    )


def _dispatch_job(
    job_name: str,
    handler: Callable[[Dict[str, Any], int, datetime], Dict[str, Any]],
):
    payload: Dict[str, Any]
    started: datetime
    job_id: int
    try:
        ensure_superuser()
        payload = request.get_json(silent=True) or {}
        started = datetime.now(timezone.utc)
        job_id = create_job_record(job_name, started_at=started, details={"request": payload})
        _job_status[job_id] = "running"
    except PermissionError as error:
        return handle_permission_error(error)
    except Exception as error:
        print(f"Admin job dispatch error for {job_name}: {error}")
        return jsonify({"detail": "Maintenance action failed"}), 500

    def run_job():
        try:
            if _job_status.get(job_id) == "cancelled":
                raise CancelledError()
            result = handler(payload, job_id, started)
            _job_results[job_id] = {
                "status": "success",
                "result": result,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            _job_status[job_id] = "success"
        except CancelledError:
            _job_results[job_id] = {
                "status": "cancelled",
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            _job_status[job_id] = "cancelled"
        except Exception as error:  # pragma: no cover - background task diagnostics
            try:
                maintenance_tasks.log_job_result(
                    job_name,
                    "failed",
                    {"error": str(error)},
                    started,
                    job_id=job_id,
                )
            except Exception:
                pass
            _job_results[job_id] = {
                "status": "failed",
                "error": str(error),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            _job_status[job_id] = "failed"
            raise
        finally:
            _job_futures.pop(job_id, None)
            _job_status.setdefault(job_id, "completed")

    try:
        future = _executor.submit(run_job)
        _job_futures[job_id] = future
    except Exception as error:  # pragma: no cover - executor diagnostics
        try:
            maintenance_tasks.log_job_result(
                job_name,
                "failed",
                {"error": str(error)},
                started,
                job_id=job_id,
            )
        except Exception:
            pass
        print(f"Failed to submit job {job_name}: {error}")
        _job_status[job_id] = "failed"
        return jsonify({"detail": "Unable to queue maintenance job"}), 500

    return (
        jsonify(
            {
                "job_id": job_id,
                "status": "queued",
                "submitted_at": started.isoformat(),
            }
        ),
        202,
    )
