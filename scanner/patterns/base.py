from abc import ABC, abstractmethod
from scanner.models import PatternConfig, PatternSignal, Candle

class BasePattern(ABC):
    """
    Abstract base class every pattern must inherit from.
    """
    config: PatternConfig

    @abstractmethod
    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        """Run the detection algorithm."""
        ...

    @abstractmethod
    def score(
        self,
        signal_strength: float,
        volume_score:    float,
        rr_score:        float,
        stage2_score:    float,
        rs_score:        float,
    ) -> float:
        """Compute pattern-specific composite score 0–100."""
        ...

    def is_eligible(self, candles: list[Candle]) -> bool:
        """Candle count guard."""
        return len(candles) >= self.config.min_candles

    def get_meta(self) -> dict:
        """Return UI metadata dict."""
        return {
            "name":        self.config.name,
            "full_name":   self.config.full_name,
            "color":       self.config.color,
            "icon":        self.config.icon,
            "description": self.config.description,
            "timeframe":   self.config.timeframe,
            "version":     self.config.version,
        }

    @property
    @abstractmethod
    def judge_prompt(self) -> str:
        """Pattern-specific section for the Groq judge prompt."""
        ...
