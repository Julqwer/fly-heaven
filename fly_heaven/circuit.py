"""Appetitive candidate circuit for FLY HEAVEN.

Experimental engineering model:
- PAM07 is used as the positive reinforcement DAN population.
- MBON05 is used as the candidate output compartment.
- Plasticity is restricted to existing positive KC -> MBON05 edges.

This does not claim that the simulation reproduces subjective reward
or the full biological mechanism of appetitive learning.
"""

import numpy as np
from doom_learning.common import annotations, digest


def identify(brain):
    a = annotations(brain.ids)
    types = a.type.fillna("")

    # Kenyon cells
    kc = np.flatnonzero(types.str.startswith("KC")).astype(np.int32)

    # Candidate appetitive output: MBON05, both hemispheres
    mb = np.flatnonzero(types.eq("MBON05")).astype(np.int32)

    # Candidate appetitive DAN population: PAM07
    dan = np.flatnonzero(types.eq("PAM07")).astype(np.int32)

    if len(mb) != 2:
        raise ValueError(f"Expected two MBON05 cells, found {len(mb)}")

    if len(dan) == 0:
        raise ValueError("No PAM07 cells found")

    # All existing KC -> MBON05 edges
    edges = np.flatnonzero(np.isin(brain.post, mb)).astype(np.int64)
    pre = np.searchsorted(brain.ptr, edges, side="right") - 1

    keep = np.isin(pre, kc)
    edges = edges[keep]
    pre = pre[keep].astype(np.int32)

    if len(edges) == 0:
        raise ValueError("No KC -> MBON05 edges found")

    if np.any(brain.weight[edges] <= 0):
        raise ValueError("Expected positive KC -> MBON05 baseline weights")

    # Estimate DAN participation from reconstructed PAM07 -> MBON05 contacts.
    contact = np.zeros((len(dan), len(mb)), dtype=np.float32)

    for d, i in enumerate(dan):
        for m, j in enumerate(mb):
            ix = (
                np.flatnonzero(
                    brain.post[brain.ptr[i] : brain.ptr[i + 1]] == j
                )
                + brain.ptr[i]
            )
            contact[d, m] = np.abs(brain.weight[ix]).sum()

    if np.any(contact.sum(axis=0) <= 0):
        raise ValueError("Missing PAM07 -> MBON05 anatomical support")

    # Normalize PAM07 contribution separately for each MBON05.
    gain = (
        contact / contact.sum(axis=0)
    )[..., np.searchsorted(mb, brain.post[edges])].copy()

    kc_mask = np.zeros(brain.n, dtype=np.uint8)
    kc_mask[kc] = 1

    dan_index = np.full(brain.n, -1, dtype=np.int8)
    dan_index[dan] = np.arange(len(dan))

    report = {
        "model": "fly-heaven-appetitive-v1",
        "kc_count": int(len(kc)),
        "pam07_count": int(len(dan)),
        "mbon05_count": int(len(mb)),
        "plastic_edges": int(len(edges)),
        "plastic_edge_sha256": digest(edges),
        "selection": "All existing positive KC-to-MBON05 edges",
        "reinforcement": "PAM07 candidate appetitive DAN population",
    }

    return {
        "kc": kc,
        "mb": mb,
        "dan": dan,
        "edges": edges,
        "pre": pre,
        "gain": gain.astype(np.float32),
        "kc_mask": kc_mask,
        "dan_index": dan_index,
        "report": report,
    }
