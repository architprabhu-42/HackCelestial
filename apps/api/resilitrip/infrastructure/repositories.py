"""Canonical, hash-checked SQLite repositories for Gate A3."""
from __future__ import annotations
import hashlib, json, sqlite3
from resilitrip.domain.generic_trip import GenericTripAggregate
from resilitrip.domain.models import PlanEvaluation, PlannerResult, ServiceCatalog, TimingReplayEvent, TripAggregate, TripLifecycle, TripMode
from resilitrip.domain.semantic_snapshots import EvaluationSnapshotHistory, ImmutableEvaluationSnapshot

def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
def content_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()
def snapshot_hash(trip: TripAggregate) -> str:
    return content_hash(trip.model_dump(mode="json"))
def generic_snapshot_hash(trip: GenericTripAggregate) -> str:
    return content_hash(trip.model_dump(mode="json"))
def _checked(payload: str, digest: str, model):
    if hashlib.sha256(payload.encode()).hexdigest() != digest: raise RuntimeError("INTERNAL_DATA_INTEGRITY_ERROR")
    return model.model_validate_json(payload)

class CatalogRepository:
    def __init__(self, connection): self.connection=connection
    def seed(self, catalog: ServiceCatalog) -> None:
        payload=canonical_json(catalog.model_dump(mode="json")); digest=hashlib.sha256(payload.encode()).hexdigest()
        row=self.connection.execute("SELECT canonical_json,snapshot_hash FROM catalogs WHERE catalog_version=?",(catalog.catalog_version,)).fetchone()
        if row and row != (payload,digest): raise ValueError("CATALOG_VERSION_CONFLICT")
        self.connection.execute("INSERT OR IGNORE INTO catalogs VALUES (?,?,?,?)",(catalog.catalog_version,catalog.scenario_id or "manual",payload,digest))
    def get(self, version: str) -> ServiceCatalog:
        row=self.connection.execute("SELECT canonical_json,snapshot_hash FROM catalogs WHERE catalog_version=?",(version,)).fetchone()
        if not row: raise KeyError(version)
        return _checked(row[0],row[1],ServiceCatalog)

class TripRepository:
    def __init__(self, connection): self.connection=connection
    def create_initial(self, trip: TripAggregate) -> None:
        payload=canonical_json(trip.model_dump(mode="json")); digest=hashlib.sha256(payload.encode()).hexdigest()
        self.connection.execute("INSERT INTO trips (trip_id,current_version,catalog_version,scenario_id,trip_mode,trip_lifecycle) VALUES (?,?,?,?,?,?)",(trip.id,trip.version,trip.catalog_version,trip.scenario_id or "manual",str(trip.mode),str(trip.lifecycle)))
        self.connection.execute("INSERT INTO trip_versions VALUES (?,?,?,?,?)",(trip.id,trip.version,payload,digest,"created"))
    def exists(self, trip_id: str) -> bool:
        return self.connection.execute("SELECT 1 FROM trips WHERE trip_id=?",(trip_id,)).fetchone() is not None
    def get_initial(self, trip_id: str) -> TripAggregate: return self.get_version(trip_id,1)
    def get_current(self, trip_id: str) -> TripAggregate:
        row=self.connection.execute("SELECT current_version FROM trips WHERE trip_id=?",(trip_id,)).fetchone()
        if not row: raise KeyError(trip_id)
        return self.get_version(trip_id,row[0])
    def get_version(self, trip_id: str, version: int) -> TripAggregate:
        row=self.connection.execute("SELECT versions.snapshot_json,versions.snapshot_hash,trips.trip_mode,trips.trip_lifecycle FROM trip_versions AS versions JOIN trips ON trips.trip_id=versions.trip_id WHERE versions.trip_id=? AND versions.version=?",(trip_id,version)).fetchone()
        if not row: raise KeyError(trip_id)
        snapshot = _checked(row[0],row[1],TripAggregate)
        return snapshot.model_copy(update={"mode": TripMode(row[2]), "lifecycle": TripLifecycle(row[3])})
    def save_version(self, prior_version: int, trip: TripAggregate) -> int:
        if trip.version != prior_version+1: raise ValueError("VERSION_CONFLICT")
        payload=canonical_json(trip.model_dump(mode="json")); digest=hashlib.sha256(payload.encode()).hexdigest()
        cursor=self.connection.execute("UPDATE trips SET current_version=?,catalog_version=?,trip_mode=?,trip_lifecycle=? WHERE trip_id=? AND current_version=?",(trip.version,trip.catalog_version,str(trip.mode),str(trip.lifecycle),trip.id,prior_version))
        if cursor.rowcount != 1: raise ValueError("VERSION_CONFLICT")
        self.connection.execute("INSERT INTO trip_versions VALUES (?,?,?,?,?)",(trip.id,trip.version,payload,digest,trip.last_mutation_kind))
        cursor=self.connection.execute("UPDATE plans SET lifecycle_status='stale' WHERE trip_id=? AND lifecycle_status='preview'",(trip.id,))
        return cursor.rowcount


class GenericTripRepository:
    """Append-only, hash-checked persistence for the isolated R1 aggregate."""

    def __init__(self, connection): self.connection = connection

    @staticmethod
    def _snapshot_payload(snapshot: ImmutableEvaluationSnapshot) -> tuple[str, str]:
        payload = canonical_json(snapshot.model_dump(mode="json"))
        return payload, hashlib.sha256(payload.encode()).hexdigest()

    def _append_semantic_snapshots(self, trip: GenericTripAggregate) -> None:
        for snapshot in trip.semantic_snapshots.snapshots:
            payload, digest = self._snapshot_payload(snapshot)
            existing = self.connection.execute(
                "SELECT snapshot_json,snapshot_hash FROM generic_semantic_snapshots WHERE trip_id=? AND snapshot_id=?",
                (trip.id, snapshot.id),
            ).fetchone()
            if existing is None:
                self.connection.execute(
                    "INSERT INTO generic_semantic_snapshots VALUES (?,?,?,?,?)",
                    (trip.id, snapshot.id, snapshot.trip_version, payload, digest),
                )
            elif existing != (payload, digest):
                raise ValueError("SEMANTIC_SNAPSHOT_CONFLICT")

    def create_initial(self, trip: GenericTripAggregate) -> None:
        if trip.version != 1: raise ValueError("INITIAL_VERSION_CONFLICT")
        payload = canonical_json(trip.model_dump(mode="json")); digest = hashlib.sha256(payload.encode()).hexdigest()
        self.connection.execute("SAVEPOINT generic_trip_create")
        try:
            self.connection.execute(
                "INSERT INTO generic_trips (trip_id,current_version,trip_mode,trip_lifecycle,scenario_id,truth_label) VALUES (?,?,?,?,?,?)",
                (trip.id, trip.version, str(trip.mode), str(trip.lifecycle), trip.scenario_id, trip.truth_label),
            )
            self.connection.execute(
                "INSERT INTO generic_trip_versions VALUES (?,?,?,?,?)",
                (trip.id, trip.version, payload, digest, "created"),
            )
            self._append_semantic_snapshots(trip)
        except Exception:
            self.connection.execute("ROLLBACK TO generic_trip_create")
            raise
        finally:
            self.connection.execute("RELEASE generic_trip_create")

    def get_version(self, trip_id: str, version: int) -> GenericTripAggregate:
        row = self.connection.execute(
            "SELECT snapshot_json,snapshot_hash FROM generic_trip_versions WHERE trip_id=? AND version=?",
            (trip_id, version),
        ).fetchone()
        if not row: raise KeyError(trip_id)
        return _checked(row[0], row[1], GenericTripAggregate)

    def get_current(self, trip_id: str) -> GenericTripAggregate:
        row = self.connection.execute("SELECT current_version FROM generic_trips WHERE trip_id=?", (trip_id,)).fetchone()
        if not row: raise KeyError(trip_id)
        return self.get_version(trip_id, row[0])

    def get_semantic_history(self, trip_id: str) -> EvaluationSnapshotHistory:
        rows = self.connection.execute(
            "SELECT snapshot_json,snapshot_hash FROM generic_semantic_snapshots WHERE trip_id=? ORDER BY rowid",
            (trip_id,),
        ).fetchall()
        return EvaluationSnapshotHistory(snapshots=tuple(_checked(row[0], row[1], ImmutableEvaluationSnapshot) for row in rows))

    def save_version(self, prior_version: int, trip: GenericTripAggregate) -> None:
        if trip.version != prior_version + 1: raise ValueError("VERSION_CONFLICT")
        payload = canonical_json(trip.model_dump(mode="json")); digest = hashlib.sha256(payload.encode()).hexdigest()
        self.connection.execute("SAVEPOINT generic_trip_save")
        try:
            cursor = self.connection.execute(
                "UPDATE generic_trips SET current_version=?,trip_mode=?,trip_lifecycle=?,scenario_id=?,truth_label=? "
                "WHERE trip_id=? AND current_version=?",
                (trip.version, str(trip.mode), str(trip.lifecycle), trip.scenario_id, trip.truth_label, trip.id, prior_version),
            )
            if cursor.rowcount != 1: raise ValueError("VERSION_CONFLICT")
            self.connection.execute(
                "INSERT INTO generic_trip_versions VALUES (?,?,?,?,?)",
                (trip.id, trip.version, payload, digest, "updated"),
            )
            self._append_semantic_snapshots(trip)
        except Exception:
            self.connection.execute("ROLLBACK TO generic_trip_save")
            raise
        finally:
            self.connection.execute("RELEASE generic_trip_save")

class EventRepository:
    def __init__(self, connection): self.connection=connection
    def find(self, trip_id,event_id): return self.connection.execute("SELECT command_json,command_hash,applied_version FROM events WHERE trip_id=? AND event_id=?",(trip_id,event_id)).fetchone()
    def latest_sequence(self, trip_id: str, source_id: str) -> int | None:
        row = self.connection.execute(
            "SELECT MAX(source_sequence) FROM events WHERE trip_id=? AND source_id=?",
            (trip_id, source_id),
        ).fetchone()
        return row[0] if row and row[0] is not None else None
    def add(self, trip_id: str, event: TimingReplayEvent, version: int):
        payload=canonical_json(event.model_dump(mode="json")); digest=hashlib.sha256(payload.encode()).hexdigest()
        self.connection.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",(trip_id,event.event_id,event.source_id,event.source_sequence,payload,digest,version))

class PlanRepository:
    def __init__(self, connection): self.connection=connection
    def save_result(self, result: PlannerResult):
        payload=canonical_json(result.model_dump(mode="json")); digest=hashlib.sha256(payload.encode()).hexdigest()
        self.connection.execute("INSERT OR REPLACE INTO planner_runs (run_id,trip_id,trip_version,catalog_version,result_json,result_hash) VALUES (?,?,?,?,?,?)",(result.run_id,result.trip_id,result.trip_version,result.catalog_version,payload,digest))
        for plan in (*result.feasible_plans,*result.uncertain_plans,*result.rejected_plans):
            data=canonical_json(plan.model_dump(mode="json")); hashed=hashlib.sha256(data.encode()).hexdigest()
            self.connection.execute("INSERT OR REPLACE INTO plans VALUES (?,?,?,?,?,?,?,?)",(plan.trip_id,plan.id,plan.trip_version,plan.catalog_version,data,hashed,plan.lifecycle_status.value,int(result.search_complete)))
    def get(self, trip_id,plan_id):
        row=self.connection.execute("SELECT plan_json,plan_hash,search_complete,lifecycle_status FROM plans WHERE trip_id=? AND plan_id=?",(trip_id,plan_id)).fetchone()
        if not row: raise KeyError(plan_id)
        return _checked(row[0],row[1],PlanEvaluation),bool(row[2]),row[3]
    def set_adopted(self,trip_id,plan_id):
        self.connection.execute("UPDATE plans SET lifecycle_status='stale' WHERE trip_id=? AND plan_id<>? AND lifecycle_status='preview'",(trip_id,plan_id))
        self.connection.execute("UPDATE plans SET lifecycle_status='adopted' WHERE trip_id=? AND plan_id=?",(trip_id,plan_id))

class AdoptionRepository:
    def __init__(self,connection): self.connection=connection
    def add(self,record):
        data=canonical_json(record.model_dump(mode="json")); hashed=hashlib.sha256(data.encode()).hexdigest()
        self.connection.execute("INSERT INTO adoptions VALUES (?,?,?,?,?,?,?)",(record.id,record.trip_id,record.plan_id,record.prior_trip_version,record.resulting_trip_version,data,hashed))

def seed_catalog(connection: sqlite3.Connection,catalog: ServiceCatalog): CatalogRepository(connection).seed(catalog)
