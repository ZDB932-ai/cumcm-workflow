"""Read-only CUMCM metadata, dependency and declared-delivery checks.

Requires PyYAML in the project's chosen Python environment. Never runs models,
extracts archives, updates lifecycle fields, or writes reports into the project.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

try:
    import yaml
except ImportError:
    yaml = None


class InputError(ValueError):
    pass


@dataclass
class Record:
    id: str
    path: Path
    kind: str
    meta: dict
    body: str
    prompt: Record | None = None


def text_file(path):
    return path.read_text(encoding="utf-8-sig")


def metadata(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, False
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise InputError("Unterminated YAML frontmatter")
    try:
        data = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        raise InputError(f"Invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise InputError("Frontmatter must be a mapping")
    return data, "\n".join(lines[end + 1:]), True


def strings(value, field):
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
        raise InputError(f"{field} must be a list of nonempty strings")
    return value


def objects(value, field):
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(x, dict) for x in value):
        raise InputError(f"{field} must be a list of objects")
    return value


TASK_REF_FIELDS = ("depends_on", "context_refs", "evidence_refs", "decision_refs", "issue_refs")


def task_fields(body):
    """Read declared fields, including YAML blocks and legacy semicolon summaries."""
    fields = {}
    names = "|".join((*TASK_REF_FIELDS, "prompt_ref", "prompt_version", "inputs"))
    pattern = re.compile(r"(?:^|[;；])\s*(?:-\s+)?(" + names + r")\s*:\s*([^;；]*)")
    lines = body.splitlines()
    for i, line in enumerate(lines):
        for match in pattern.finditer(line):
            key, raw = match.groups()
            raw = raw.strip()
            if not raw:
                block = []
                base_indent = len(line) - len(line.lstrip())
                for following in lines[i + 1:]:
                    # Empty/comment lines do not terminate a YAML collection.
                    if not following.strip() or following.lstrip().startswith("#"):
                        block.append(following)
                        continue
                    indent = len(following) - len(following.lstrip())
                    if indent <= base_indent and not following.lstrip().startswith("- "):
                        break
                    block.append(following)
                raw = "\n".join(block)
            try:
                value = yaml.safe_load(raw) if raw else None
            except yaml.YAMLError as exc:
                raise InputError(f"Invalid task {key}: {exc}") from exc
            if key in TASK_REF_FIELDS and isinstance(value, str):
                # Old prose summaries are locators, never execution instructions.
                value = re.findall(r"\b(?:TASK|DEC|OVR|RES|MOD|EXP|FACT|ISSUE|CLAIM|FIG)-[A-Za-z0-9-]+", value)
                if not value:
                    raise InputError(f"Task {key} contains no recognizable reference ID")
            if key in fields and fields[key] != value:
                raise InputError(f"Conflicting task field: {key}")
            fields[key] = value
    return fields


class Audit:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise InputError("Project root does not exist")
        self.findings = []
        self.records = {}
        self.ambiguous = set()
        self.hash_cache = {}
        self.scanned = 0

    def label(self, path):
        try:
            return Path(path).relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def add(self, severity, code, path, message):
        finding = dict(severity=severity, code=code, location=self.label(path), message=message)
        if finding not in self.findings:
            self.findings.append(finding)

    def path(self, value):
        if not isinstance(value, str) or not value:
            raise InputError("A nonempty local path is required")
        p = Path(value.replace("\\", "/"))
        p = (p if p.is_absolute() else self.root / p).resolve()
        if not p.is_relative_to(self.root):
            raise InputError(f"Path is outside project root: {value}")
        return p

    def register(self, record):
        if record.id in self.records:
            self.ambiguous.add(record.id)
            self.add("error", "duplicate_id", record.path,
                     f"{record.id} also defined in {self.label(self.records[record.id].path)}")
        else:
            self.records[record.id] = record

    def index(self):
        # Scan metadata in declared memory folders; never crawl result data or chat logs.
        for folder, kind in [("decisions", "decision"), ("evidence", "evidence"),
                             ("issues", "issue"), ("checkpoints", "checkpoint")]:
            for raw in sorted((self.root / "memory" / folder).glob("*.md")):
                try:
                    p = self.path(str(raw))
                    meta, body, present = metadata(text_file(p))
                    self.scanned += 1
                    rid = meta.get("id", p.stem)
                    if not isinstance(rid, str) or not rid:
                        raise InputError("id must be a nonempty string")
                    if not present:
                        self.add("warning", "legacy_metadata", p,
                                 "No frontmatter; filename is a locator only, status is unknown")
                    self.register(Record(rid, p, kind, meta, body))
                except (InputError, OSError, UnicodeError) as exc:
                    self.add("error", "metadata_read", raw, str(exc))
        tasks_path = self.root / "memory/active/TASKS.md"
        if not tasks_path.is_file():
            self.add("error", "missing_tasks", tasks_path, "Current task index is missing")
            return
        try:
            tasks_path = self.path(str(tasks_path))
            text = text_file(tasks_path)
            headings = list(re.finditer(r"(?m)^## (TASK-[A-Za-z0-9-]+)\s*$", text))
            for i, match in enumerate(headings):
                body = text[match.end():headings[i + 1].start() if i + 1 < len(headings) else len(text)]
                self.register(Record(match[1], tasks_path, "task", {}, body))
            # Exact task files are optional archived definitions; an index locator is not a definition.
            for raw in sorted((self.root / "memory/archive").glob("TASK-*.md")):
                p = self.path(str(raw))
                meta, body, _ = metadata(text_file(p))
                rid = meta.get("id", p.stem)
                if not isinstance(rid, str) or not rid:
                    raise InputError("Archived task id must be a nonempty string")
                old = self.records.get(rid)
                if old and old.kind == "task" and self.label(p) in old.body:
                    # The active index explicitly delegates its definition to this exact file.
                    self.records[rid] = Record(rid, p, "task", meta, body)
                else:
                    self.register(Record(rid, p, "task", meta, body))
        except (InputError, OSError, UnicodeError) as exc:
            self.add("error", "task_read", tasks_path, str(exc))

        for r in self.records.values():
            if r.kind != "task":
                continue
            try:
                for key, value in task_fields(r.body).items():
                    if key in r.meta and r.meta[key] != value:
                        raise InputError(f"Frontmatter/body conflict for {r.id}: {key}")
                    r.meta[key] = value
            except InputError as exc:
                self.add("error", "task_fields", r.path, str(exc))
            if "prompt_ref" in r.meta:
                try:
                    p = self.path(r.meta["prompt_ref"])
                    meta, body, present = metadata(text_file(p))
                    if not present or meta.get("id") != r.id:
                        raise InputError(f"Prompt must have frontmatter id={r.id}")
                    if "prompt_version" in r.meta and meta.get("prompt_version") != r.meta["prompt_version"]:
                        raise InputError(f"Prompt version differs for {r.id}")
                    # Keep immutable assignment separate from mutable task control fields.
                    r.prompt = Record(r.id, p, "prompt", meta, body)
                except (InputError, OSError, UnicodeError) as exc:
                    self.add("error", "prompt_read", r.path, f"{r.id}: {exc}")

    def references(self, record, dependency_only=False, for_scope=False):
        refs = list(strings(record.meta.get("depends_on"), "depends_on"))
        if record.prompt:
            refs += self.references(record.prompt, dependency_only, for_scope)
        if not dependency_only:
            # Blocking links are integrity references, not data dependencies or
            # a reason to expand a scoped task into unrelated blocked work.
            if record.kind == "issue" and not for_scope:
                refs += strings(record.meta.get("blocks"), "blocks")
            fields = ("evidence_refs", "decision_refs", "issue_refs")
            for field in fields if for_scope else ("related", *fields):
                refs += strings(record.meta.get(field), field)
            for field in ("producer_task",) if for_scope else ("producer_task", "supersedes", "superseded_by"):
                value = record.meta.get(field)
                if value is not None:
                    if not isinstance(value, str):
                        raise InputError(f"{field} must be a string or null")
                    if value:
                        refs.append(value)
            context = record.meta.get("context_refs", [])
            if not isinstance(context, list):
                raise InputError("context_refs must be a list")
            for value in context:
                rid = value if isinstance(value, str) else value.get("id") if isinstance(value, dict) else None
                if not isinstance(rid, str) or not rid:
                    raise InputError("context_refs entries require an ID")
                refs.append(rid)
        normalized = []
        for value in refs:
            match = re.match(r"^([A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+)(?=[^A-Za-z0-9-]|$)", value)
            if value not in self.records and match and match[1] in self.records:
                self.add("warning", "legacy_reference", record.path,
                         f"Resolved {value!r} as {match[1]}; inspect the attached scope explanation")
                normalized.append(match[1])
            else:
                normalized.append(value)
        return list(dict.fromkeys(normalized))

    def graph(self):
        graph = {}
        for rid, r in self.records.items():
            try:
                graph[rid] = self.references(r, dependency_only=True)
            except InputError as exc:
                self.add("error", "reference_shape", r.path, str(exc))
                graph[rid] = []
        # Kahn's algorithm handles long chains without a recursion limit.
        indegree = {rid: 0 for rid in graph}
        reverse = defaultdict(list)
        for rid, deps in graph.items():
            for dep in deps:
                if dep in graph:
                    indegree[rid] += 1
                    reverse[dep].append(rid)
        queue = deque(rid for rid, n in indegree.items() if n == 0)
        while queue:
            for child in reverse[queue.popleft()]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        unresolved = [rid for rid, n in indegree.items() if n]
        if unresolved:
            self.add("error", "dependency_cycle", self.root / "memory",
                     "Cycle or dependency on a cycle: " + ", ".join(sorted(unresolved)))
        return graph

    def digest(self, path, member=None):
        key = (str(path), member)
        if key not in self.hash_cache:
            digest = hashlib.sha256()
            if member is None:
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(block)
            else:
                with zipfile.ZipFile(path) as archive:
                    if archive.namelist().count(member) != 1:
                        raise InputError(f"ZIP member absent or ambiguous: {member}")
                    with archive.open(member) as stream:
                        for block in iter(lambda: stream.read(1024 * 1024), b""):
                            digest.update(block)
            self.hash_cache[key] = digest.hexdigest()
        return self.hash_cache[key]

    def artifact(self, item, location, hashes=False, require_hash=False):
        try:
            p = self.path(item.get("path"))
            if not p.is_file():
                self.add("error", "missing_artifact", location, f"Missing file: {self.label(p)}")
                return
            expected = item.get("sha256")
            member = item.get("member")
            if member is not None:
                if not isinstance(member, str) or not member or "\\" in member or ":" in member or PurePosixPath(member).is_absolute() or ".." in PurePosixPath(member).parts:
                    raise InputError("ZIP member must be a relative POSIX file path")
                with zipfile.ZipFile(p) as archive:
                    if archive.namelist().count(member) != 1 or archive.getinfo(member).is_dir():
                        raise InputError(f"ZIP member absent, ambiguous or directory: {member}")
            if expected is not None and not (isinstance(expected, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected)):
                raise InputError("sha256 must contain exactly 64 hexadecimal characters")
            if require_hash and not expected:
                self.add("warning", "unversioned_artifact", location, f"No SHA-256 for {item['path']}")
            if hashes and expected and self.digest(p, member) != expected.lower():
                self.add("error", "hash_mismatch", location,
                         f"Declared version differs: {item['path']}" + (f"!{member}" if member else ""))
        except (InputError, OSError, KeyError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as exc:
            self.add("error", "artifact_read", location, str(exc))

    def status(self, task=None, hashes=False):
        self.index()
        self.graph()
        selected = set(self.records)
        if task:
            selected = set()
            queue = [task]
            while queue:
                rid = queue.pop()
                if rid in selected:
                    continue
                selected.add(rid)
                r = self.records.get(rid)
                if r:
                    try:
                        queue.extend(self.references(r, for_scope=True))
                    except InputError as exc:
                        self.add("error", "reference_shape", r.path, str(exc))
            if task not in self.records:
                self.add("error", "missing_task", self.root / "memory", task)
        state_path = self.root / "memory/active/STATE.md"
        try:
            p = self.path(str(state_path))
            text = text_file(p)
            state, _, present = metadata(text)
            if not present:
                self.add("warning", "legacy_state", p, "State has no structured frontmatter")
            gate = state.get("gate")
            if gate is not None and gate not in tuple(f"G{i}" for i in range(1, 9)):
                self.add("error", "invalid_gate", p,
                         "gate must be null (no accepted milestone) or G1 through G8")
            if len(text.encode("utf-8")) > 8192 or len(text.splitlines()) > 150:
                self.add("warning", "state_budget", p,
                         f"{len(text.encode('utf-8'))} bytes / {len(text.splitlines())} lines; semantic compaction suggested")
            for field in ("active_tasks", "active_overrides", "critical_issues"):
                for rid in strings(state.get(field), field):
                    if rid not in self.records:
                        self.add("error", "missing_state_reference", p, f"{field}: {rid}")
            checkpoint = state.get("checkpoint_ref")
            if checkpoint and checkpoint not in self.records:
                self.add("error", "missing_state_reference", p, f"checkpoint_ref: {checkpoint}")
        except (InputError, OSError, UnicodeError) as exc:
            self.add("error", "state_read", state_path, str(exc))
        allowed = {"decision": {"active", "superseded", "rejected"},
                   "issue": {"open", "investigating", "resolved", "wontfix"},
                   "evidence": {"candidate", "verified", "stale", "rejected", "obsolete"}}
        for rid in sorted(selected & self.records.keys()):
            r = self.records[rid]
            status = r.meta.get("status")
            statuses = {"active", "expired", "revoked"} if r.meta.get("type") == "override" else allowed.get(r.kind)
            if statuses and status not in statuses:
                alias = (r.kind, status) in {("issue", "closed"), ("decision", "obsolete")}
                self.add("warning" if alias or status is None else "error",
                         "legacy_status" if alias or status is None else "invalid_status", r.path,
                         f"status={status!r}; verify meaning without rewriting history")
            try:
                for dep in self.references(r):
                    if dep not in self.records:
                        self.add("error", "missing_reference", r.path, dep)
                for item in objects(r.meta.get("artifacts"), "artifacts"):
                    self.artifact(item, r.path, hashes)
                if r.kind == "task":
                    for source in (r, r.prompt) if r.prompt else (r,):
                        for item in objects(source.meta.get("inputs"), "inputs"):
                            item = dict(item)
                            version = item.get("version")
                            if "sha256" not in item and isinstance(version, str) and re.fullmatch(r"[0-9a-fA-F]{64}", version):
                                item["sha256"] = version
                            self.artifact(item, source.path, hashes)
                if r.kind == "evidence" and status == "verified":
                    v = r.meta.get("validation")
                    needed = ("checked_by", "checked_at", "method", "scope", "checks_run", "outcome")
                    if not isinstance(v, dict) or any(not v.get(k) for k in needed):
                        self.add("warning", "validation_record_incomplete", r.path,
                                 "Verified label lacks structured validation details; inspect original evidence")
                    if isinstance(v, dict):
                        outcome = v.get("outcome")
                        if isinstance(outcome, str):
                            outcome = outcome.strip().lower()
                        if outcome in ("failed", "fail", "not_checked", "pending", "unknown"):
                            self.add("error", "validation_status_conflict", r.path,
                                     f"verified contradicts validation.outcome={outcome}; run_status is separate from validation outcome")
                        elif outcome not in ("passed", "pass"):
                            self.add("warning", "validation_outcome_review", r.path,
                                     "Validation outcome is missing or nonstandard; inspect its scope and meaning")
            except InputError as exc:
                self.add("error", "record_shape", r.path, str(exc))
        return {"selected_records": sorted(selected), "metadata_files_scanned": self.scanned,
                "hashes_checked": hashes, "ambiguous_ids": sorted(self.ambiguous)}

    def manifest(self, name):
        p = self.path(name)
        try:
            data = json.loads(text_file(p))
        except (ValueError, OSError) as exc:
            raise InputError(f"Cannot load manifest: {exc}") from exc
        if not isinstance(data, dict) or data.get("format") != "cumcm-delivery-v1":
            raise InputError("Manifest format must be cumcm-delivery-v1")
        items = objects(data.get("artifacts"), "artifacts")
        if not items:
            raise InputError("Manifest artifacts cannot be empty")
        ids = set()
        for item in items:
            rid = item.get("id")
            if not isinstance(rid, str) or not rid or rid in ids:
                raise InputError("Manifest artifact IDs must be nonempty and unique")
            ids.add(rid)
        return p, items

    def delivery(self, name):
        p, items = self.manifest(name)
        for item in items:
            state = item.get("sync_status", "unverified")
            if state not in {"matching", "stale", "unverified", "excluded"}:
                raise InputError(f"Invalid sync_status: {state}")
            required = item.get("required", True)
            if not isinstance(required, bool):
                raise InputError("required must be boolean")
            if state == "excluded":
                if not item.get("reason"):
                    self.add("error", "missing_exclusion_reason", p, item["id"])
                self.add("error" if required else "warning", "excluded_delivery", p,
                         f"{item['id']} excluded; it has not been verified")
                continue
            self.artifact(item, p, hashes=True, require_hash=True)
            sources = objects(item.get("based_on"), "based_on")
            if not sources:
                self.add("warning", "source_mapping_missing", p, item["id"])
            for source in sources:
                self.artifact(source, p, hashes=True, require_hash=True)
            if state != "matching":
                self.add("error" if state == "stale" else "warning", "delivery_sync", p,
                         f"{item['id']}: {state}")
        return {"manifest": self.label(p), "artifacts_declared": len(items), "hashes_checked": True}

    def impact(self, name, manifest=None):
        target = self.path(name)  # It may have been deleted; path identity is still meaningful.
        self.index()
        graph = self.graph()
        direct = set()
        for rid, r in self.records.items():
            try:
                for item in objects(r.meta.get("artifacts"), "artifacts"):
                    if self.path(item.get("path")) == target:
                        direct.add(rid)
                if r.kind == "task":
                    if r.prompt and r.prompt.path == target:
                        direct.add(rid)
                    for source in (r, r.prompt) if r.prompt else (r,):
                        for item in objects(source.meta.get("inputs"), "inputs"):
                            if self.path(item.get("path")) == target:
                                direct.add(rid)
            except InputError as exc:
                self.add("error", "artifact_reference", r.path, str(exc))
        affected = set(direct)
        reverse = defaultdict(set)
        for rid, deps in graph.items():
            for dep in deps:
                reverse[dep].add(rid)
                if dep not in self.records:
                    self.add("error", "missing_reference", self.records[rid].path, dep)
        queue = deque(direct)
        while queue:
            for child in reverse[queue.popleft()] - affected:
                affected.add(child)
                queue.append(child)
        paths = {target}
        for rid in affected:
            for item in objects(self.records[rid].meta.get("artifacts"), "artifacts"):
                try:
                    paths.add(self.path(item.get("path")))
                except InputError:
                    pass  # Reported during direct scan above.
        consumers = []
        if manifest:
            _, items = self.manifest(manifest)
            pending = list(items)
            while pending:
                next_round = []
                for item in pending:
                    own = self.path(item.get("path"))
                    sources = objects(item.get("based_on"), "based_on")
                    if own in paths or any(self.path(s.get("path")) in paths for s in sources):
                        consumers.append({"id": item["id"], "path": item["path"],
                                          "sync_status": item.get("sync_status", "unverified")})
                        paths.add(own)
                    else:
                        next_round.append(item)
                if len(next_round) == len(pending):
                    break
                pending = next_round
        if not direct and not consumers:
            self.add("warning", "untracked_artifact", target,
                     "No declared dependency found; this does not establish absence of impact")
        return {"artifact": self.label(target), "direct_records": sorted(direct),
                "affected_records": sorted(affected), "consumers": consumers,
                "action": "Review these dependencies; no lifecycle or file was changed"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("status", "impact", "delivery"):
        p = sub.add_parser(command)
        p.add_argument("--root", required=True)
        if command == "status":
            p.add_argument("--task")
            p.add_argument("--hashes", action="store_true")
        elif command == "impact":
            p.add_argument("--artifact", required=True)
            p.add_argument("--manifest")
        else:
            p.add_argument("--manifest", required=True)
    args = parser.parse_args(argv)
    try:
        if yaml is None:
            raise InputError("PyYAML is unavailable; use the project environment, do not switch Python automatically")
        audit = Audit(args.root)
        if args.command == "status":
            details = audit.status(args.task, args.hashes)
        elif args.command == "impact":
            details = audit.impact(args.artifact, args.manifest)
        else:
            details = audit.delivery(args.manifest)
        counts = {level: sum(x["severity"] == level for x in audit.findings)
                  for level in ("error", "warning")}
        result = {"command": args.command, "read_only": True,
                  "outcome": "issues_found" if counts["error"] else "needs_review" if counts["warning"] else "checks_passed",
                  "summary": counts, "details": details, "findings": audit.findings,
                  "limitations": ["Only declared metadata and dependencies are checked",
                                  "No model execution, semantic consistency, complete source dependency analysis, visual QA, human verification or submission validation"]}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if counts["error"] else 0
    except (InputError, OSError, UnicodeError, TypeError) as exc:
        print(json.dumps({"outcome": "invalid_input", "read_only": True, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
