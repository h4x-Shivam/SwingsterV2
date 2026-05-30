# scanner/patterns/registry.py
from scanner.patterns.vcp.detector        import VCPPattern
from scanner.patterns.flag_pole.detector  import FlagPolePattern
from scanner.patterns.cup_handle.detector import CupHandlePattern
from scanner.patterns.breakout.detector   import BreakoutPattern
from scanner.patterns.base                import BasePattern

PATTERN_REGISTRY: dict[str, BasePattern] = {
    "VCP":        VCPPattern(),
    "FLAG_POLE":  FlagPolePattern(),
    "CUP_HANDLE": CupHandlePattern(),
    "BREAKOUT":   BreakoutPattern(),
}

def get_patterns(mode: str) -> list[BasePattern]:
    if mode == "ALL":
        return list(PATTERN_REGISTRY.values())
    if mode not in PATTERN_REGISTRY:
        valid = list(PATTERN_REGISTRY.keys()) + ["ALL"]
        raise ValueError(f"Unknown mode '{mode}'. Valid: {valid}")
    return [PATTERN_REGISTRY[mode]]

def get_all_metadata() -> list[dict]:
    return [p.get_meta() for p in PATTERN_REGISTRY.values()]

def get_pattern_config(mode: str):
    if mode == "ALL":
        raise ValueError("get_pattern_config() not valid for ALL mode.")
    return get_patterns(mode)[0].config
