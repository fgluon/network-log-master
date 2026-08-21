from __future__ import annotations

from dataclasses import dataclass


VENDOR_ALIASES = {
    "arista": "arista",
    "arista networks": "arista",
    "cisco": "cisco",
}

OS_FAMILY_ALIASES = {
    "eos": "eos",
    "arista eos": "eos",
    "nxos": "nxos",
    "nx-os": "nxos",
    "cisco nx-os": "nxos",
    "iosxr": "iosxr",
    "ios-xr": "iosxr",
    "ios xr": "iosxr",
    "cisco ios xr": "iosxr",
}


@dataclass(slots=True, frozen=True)
class PlatformHint:
    vendor: str = "unknown"
    os_family: str = "unknown"
    raw_vendor: str = ""
    raw_os_family: str = ""


def _hint_text(value: object) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    try:
        return str(value).strip()
    except Exception:
        return ""


def extract_platform_hint(
    vendor_hint: object,
    os_family_hint: object,
) -> PlatformHint:
    """
    Normalize explicit upstream platform hints.

    Unknown hints do not become trusted vendor identities.
    They remain visible as raw hint values for diagnostics.
    """

    raw_vendor = _hint_text(vendor_hint)
    raw_os_family = _hint_text(os_family_hint)

    vendor = VENDOR_ALIASES.get(
        raw_vendor.casefold(),
        "unknown",
    )

    os_family = OS_FAMILY_ALIASES.get(
        raw_os_family.casefold(),
        "unknown",
    )

    return PlatformHint(
        vendor=vendor,
        os_family=os_family,
        raw_vendor=raw_vendor,
        raw_os_family=raw_os_family,
    )
