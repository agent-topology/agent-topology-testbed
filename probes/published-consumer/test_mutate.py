"""Each case document differs from the base by exactly its named field(s)."""
import unittest

from mutate import BASE_DOCUMENT, DOCUMENT_CASES


def _diff_keys(a, b):
    return {k for k in a.keys() | b.keys() if a.get(k) != b.get(k)}


class DocumentCases(unittest.TestCase):
    def test_baseline_is_unmutated(self):
        self.assertEqual(DOCUMENT_CASES["baseline"](), BASE_DOCUMENT)

    def test_unsupported_topology_version_changes_only_that_field(self):
        doc = DOCUMENT_CASES["unsupported-topology-version"]()
        self.assertEqual(_diff_keys(BASE_DOCUMENT, doc), {"topologyVersion"})
        self.assertEqual(doc["topologyVersion"], "0.2")

    def test_unsupported_hash_algorithm_version_changes_only_that_field(self):
        doc = DOCUMENT_CASES["unsupported-hash-algorithm-version-declared"]()
        self.assertEqual(_diff_keys(BASE_DOCUMENT, doc), {"structureHash"})
        self.assertEqual(doc["structureHash"]["algorithmVersion"], "2")
        self.assertEqual(doc["structureHash"]["value"], BASE_DOCUMENT["structureHash"]["value"])

    def test_unknown_permitted_extension_adds_one_root_key(self):
        doc = DOCUMENT_CASES["unknown-permitted-extension"]()
        self.assertEqual(_diff_keys(BASE_DOCUMENT, doc), {"x-k1-probe"})
        self.assertEqual(doc["x-k1-probe"], "case-4-string-value")

    def test_malformed_extension_key_adds_one_root_key(self):
        doc = DOCUMENT_CASES["malformed-extension-key"]()
        self.assertEqual(_diff_keys(BASE_DOCUMENT, doc), {"X-k1-probe"})

    def test_invalid_extension_placement_uses_the_same_key_name_as_case_four(self):
        placed = DOCUMENT_CASES["invalid-extension-placement"]()
        permitted = DOCUMENT_CASES["unknown-permitted-extension"]()
        self.assertIn("x-k1-probe", permitted)
        self.assertIn("x-k1-probe", placed["completeness"]["gaps"][0]["element"])
        self.assertEqual(_diff_keys(BASE_DOCUMENT, placed), {"completeness"})
        self.assertEqual(placed["completeness"]["status"], "incomplete")
        self.assertEqual(placed["completeness"]["gaps"][0]["element"]["graphId"], "g")

    def test_cases_do_not_mutate_the_shared_base(self):
        DOCUMENT_CASES["unsupported-topology-version"]()
        DOCUMENT_CASES["invalid-extension-placement"]()
        self.assertEqual(BASE_DOCUMENT["topologyVersion"], "0.1")
        self.assertEqual(BASE_DOCUMENT["completeness"], {"status": "complete", "gaps": []})


if __name__ == "__main__":
    unittest.main()
