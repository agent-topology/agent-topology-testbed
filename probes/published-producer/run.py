"""Bounded D1 transformations: each case is rebuilt in two fresh processes."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil

from setup import ROOT, command, save

VARIANTS = ("base", "node-order", "edge-order", "dictionary-order", "comment", "named", "node-change", "edge-change")


def cases():
    recipes = json.loads((ROOT / "recipes.json").read_text())
    result = {}
    for shape, original in recipes.items():
        for variant in (*VARIANTS, *(("join-source-order", "independent") if shape == "join" else ())):
            recipe = copy.deepcopy(original)
            recipe.update(callable="lambda", metadata={"alpha": "one", "beta": "two"})
            if variant == "node-order": recipe["nodes"].reverse()
            if variant == "edge-order": recipe["edges"].reverse()
            if variant == "dictionary-order": recipe["metadata"] = {"beta": "two", "alpha": "one"}
            if variant == "named": recipe["callable"] = "named"
            if variant == "node-change":
                def rename(value):
                    return [rename(v) for v in value] if isinstance(value, list) else ("renamed" if value == "a" else value)
                for key in ("nodes", "edges", "joins"): recipe[key] = rename(recipe[key])
            if variant == "edge-change": recipe["edges"].append(["a", "b" if shape == "fanout" else "__end__"])
            if variant == "join-source-order": recipe["joins"][0][0].reverse()
            if variant == "independent":
                recipe["joins"] = []
                recipe["edges"] += [["a", "c"], ["b", "c"]]
            result[f"{shape}-{variant}"] = {"shape": shape, "variant": variant, "recipe": recipe}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--envs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "inputs").mkdir(); (out / "workers").mkdir()
    all_cases = cases()
    # Publish exact inputs and intended comparisons before any describe call.
    save(out / "cases.json", all_cases)
    for name, case in all_cases.items(): save(out / "inputs" / f"{name}.json", case["recipe"])
    save(out / "plan.json", {"createdAt": datetime.now(timezone.utc).isoformat(),
         "expected": "all variants retain structure/hash except node-change, edge-change, independent",
         "processesPerCasePerLanguage": 2, "describesPerCompiledGraph": 2,
         "evidenceClass": "static extraction; public spec callable checks; no framework execution"})
    records = []
    for language, extension in (("python", "py"), ("typescript", "mts")):
        source = (ROOT / f"worker.{extension}").read_text()
        for name, case in all_cases.items():
            worker = envs / language / f"worker.{extension}"
            text = source.replace("D1_UNRELATED_COMMENT", "D1_UNRELATED_COMMENT changed without executable edits") if case["variant"] == "comment" else source
            worker.write_text(text)
            (out / "workers" / f'{language}-{"comment" if case["variant"] == "comment" else "base"}.{extension}').write_text(text)
            for repeat in (1, 2):
                cmd = ([envs / "python/bin/python", "-I", worker] if language == "python" else
                       [shutil.which("node"), "--experimental-strip-types", worker])
                stdout = command(cmd + [out / "inputs" / f"{name}.json"], envs / language, out, records)
                # Keep exact stdout separately, with no metadata normalization.
                (out / f"{language}-{name}-{repeat}.json").write_text(stdout)
    sources = [p for p in ROOT.iterdir() if p.is_file()] + list((ROOT / "locks").iterdir())
    save(out / "provenance.json", {"completedAt": datetime.now(timezone.utc).isoformat(),
         "platform": platform.platform(), "machine": platform.machine(),
         "subprocessSeconds": sum(r["seconds"] for r in records),
         "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}})
    from verify import verify
    report = verify(out)
    save(out / "comparison.json", report)
    print(json.dumps(report["summary"]))
    if report["errors"]: raise SystemExit(1)


if __name__ == "__main__":
    main()
