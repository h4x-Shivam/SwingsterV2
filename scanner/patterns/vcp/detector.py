from scanner.patterns.base import BasePattern
from scanner.patterns.vcp.config import VCP_CONFIG
from scanner.models import PatternSignal, Candle

class VCPPattern(BasePattern):

    config = VCP_CONFIG

    def detect(self, candles: list[Candle], pivots: tuple) -> PatternSignal | None:
        """
        Simplified Volume-Based VCP
        Footprint: Heavy Volume Spike -> Dry Period (<50%) -> Heavy Volume Spike -> Dry Period (<50%)
        """
        try:
            if not self.is_eligible(candles):
                return None

            current_price = candles[-1].close
            lookback = 60
            recent_candles = candles[-lookback:]
            
            if len(recent_candles) < 20:
                return None

            # Calculate baseline volume
            baseline_vol = sum(c.volume for c in recent_candles) / len(recent_candles)
            if baseline_vol == 0:
                return None

            # 1. Identify Heavy Volume Spikes (Green candle, vol > 1.5 * baseline)
            spikes = []
            for i, c in enumerate(recent_candles):
                if c.close > c.open and c.volume >= baseline_vol * 1.5:
                    spikes.append({"index": i, "candle": c})

            if len(spikes) < 2:
                return None

            best_signal = None

            # 2. Find the valid A -> B -> C -> D sequence
            for i in range(len(spikes)):
                for j in range(i + 1, len(spikes)):
                    spike1 = spikes[i]
                    spike2 = spikes[j]

                    idx1 = spike1["index"]
                    idx2 = spike2["index"]

                    # Need at least 2 days of dry period between spikes
                    if idx2 - idx1 < 3:
                        continue

                    dry1_candles = recent_candles[idx1 + 1 : idx2]
                    avg_vol_dry1 = sum(c.volume for c in dry1_candles) / len(dry1_candles) if dry1_candles else float('inf')

                    # Need at least 1 day of dry period after the second spike
                    if len(recent_candles) - 1 - idx2 < 2:
                        continue

                    dry2_candles = recent_candles[idx2 + 1 :]
                    avg_vol_dry2 = sum(c.volume for c in dry2_candles) / len(dry2_candles) if dry2_candles else float('inf')

                    # The core logic: volume must dry up to <= 50% of the preceding spike
                    if avg_vol_dry1 <= spike1["candle"].volume * 0.50 and avg_vol_dry2 <= spike2["candle"].volume * 0.50:
                        
                        # Valid pattern found!
                        # Buy point is the highest price within this formation
                        formation_candles = recent_candles[idx1:]
                        buy_point = max(c.high for c in formation_candles)

                        distance_pct = ((buy_point - current_price) / current_price * 100) if current_price > 0 else 0

                        # Reject if price is too far extended above or below the buy point
                        if distance_pct > 15.0 or distance_pct < -2.0:
                            continue

                        # Score based on how exceptionally dry the volume gets
                        # Ratio of dry volume to spike volume (lower is better, max is 0.50)
                        dry1_ratio = avg_vol_dry1 / spike1["candle"].volume
                        dry2_ratio = avg_vol_dry2 / spike2["candle"].volume
                        
                        # Normalize so that 0.50 gives 50 points, 0.10 gives 90 points, etc.
                        score1 = 100.0 - (dry1_ratio * 100)
                        score2 = 100.0 - (dry2_ratio * 100)
                        strength = (score1 + score2) / 2.0
                        
                        # Bonus if current price is very tight to buy point
                        if 0 <= distance_pct <= 3.0:
                            strength += 10
                            
                        strength = max(0.0, min(strength, 100.0))

                        signal = PatternSignal(
                            name="VCP",
                            strength=strength,
                            buy_point=round(buy_point, 2),
                            distance_from_buy_pct=round(distance_pct, 2),
                            breakout_level=round(buy_point, 2),
                            pivot_high=round(buy_point, 2),
                            contraction_depth=round(distance_pct, 2), # Not really depth, but reusing field
                            contraction_count=2, # Representing 2 dry periods
                        )
                        
                        if best_signal is None or signal.strength > best_signal.strength:
                            best_signal = signal

            return best_signal

        except Exception:
            return None

    def score(
        self,
        signal_strength: float,
        volume_score:    float,
        rr_score:        float,
        stage2_score:    float,
        rs_score:        float,
    ) -> float:
        raw = (
            signal_strength * self.config.weight_signal +
            volume_score    * self.config.weight_volume +
            rr_score        * self.config.weight_rr     +
            stage2_score    * self.config.weight_stage2 +
            rs_score        * self.config.weight_rs
        )
        return round(max(0.0, min(100.0, raw)), 1)

    @property
    def judge_prompt(self) -> str:
        return """
        For Volatility Contraction Patterns (VCP), look for:
        1. A clear sequence of accumulation: heavy volume up-days followed by extreme volume dry-ups.
        2. Volume in the dry periods must be significantly lower than the preceding spikes.
        3. Tight price action preparing for a breakout.
        """
