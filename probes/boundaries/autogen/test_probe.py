"""Integrity checks for A1, including failure enforcement under Python -O."""
import asyncio
import subprocess
import sys
import unittest
from unittest.mock import patch

from probe import ROOT, collect


class Integrity(unittest.TestCase):
    def test_static_never_executes_agents_or_selector(self):
        with patch("autogen_agentchat.agents.AssistantAgent.on_messages", side_effect=RuntimeError("agent ran")), \
             patch("autogen_ext.models.replay.ReplayChatCompletionClient.create", side_effect=RuntimeError("model ran")):
            record = asyncio.run(collect(static_only=True))
        self.assertEqual(len(record["cases"]), 4)

    def test_corruption_rejected_normal_and_optimized(self):
        script = """
import asyncio, copy
from probe import collect
from verify import validate
record = asyncio.run(collect())
for mutation in ('order', 'count', 'identity', 'edge', 'selector'):
    bad = copy.deepcopy(record)
    case = bad['cases']['selector-forward']
    if mutation == 'order': case['messages'][1:] = reversed(case['messages'][1:])
    if mutation == 'count': case['messages'].append(copy.deepcopy(case['messages'][-1]))
    if mutation == 'identity': case['messages'][1]['id'] = case['messages'][0]['id']
    if mutation == 'edge': bad['cases']['graph-forward']['static']['edges'] = []
    if mutation == 'selector': case['selector_calls'] = ['beta', 'alpha']
    try:
        validate(bad)
    except ValueError:
        continue
    raise RuntimeError('accepted corruption: ' + mutation)
"""
        for flags in ([], ["-O"]):
            result = subprocess.run([sys.executable, *flags, "-c", script], cwd=ROOT,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
