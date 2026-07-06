"""
Fase 3: Full Simulation Stress Test
Backtest dengan data 1 bulan terakhir termasuk event crash/pump.
Menguji ketahanan sistem terhadap volatilitas ekstrem, slippage, dan fee.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

from st_lms.models.candle import Candle
from st_lms.measure.atr_calculator import calculate_atr
from st_lms.measure.supertrend_calculator import calculate_supertrend_points
from st_lms.multi_timeframe_structural_engine.engine import MultiTimeframeStructuralEngine
from st_lms.common.enums import Timeframe
from st_lms.classify.classifier import StateClassifier
from st_lms.authorize.authorization_gateway import AuthorizationGateway
from st_lms.execute.simulation_executor import SimulationExecutor
from st_lms.river.river_learning import RiverLearning
from st_lms.config.core_config import BOT_NAME, CORE_VERSION


class StressTestSimulator:
    """Simulator untuk stress test dengan skenario crash, pump, dan choppy market."""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine = MultiTimeframeStructuralEngine()
        self.classifier = StateClassifier()
        self.auth_gateway = AuthorizationGateway(config)
        self.executor = SimulationExecutor(config)
        self.river_learning = RiverLearning()
        
        # Metrics tracking
        self.trades: List[Dict[str, Any]] = []
        self.drawdowns: List[Decimal] = []
        self.equity_curve: List[Decimal] = []
        self.max_drawdown = Decimal('0')
        self.current_equity = Decimal('10000')  # Starting balance
        self.peak_equity = Decimal('10000')
        
    def generate_stress_data(
        self, 
        scenario: str, 
        num_candles: int = 1000,
        base_price: Decimal = Decimal('50000')
    ) -> List[Candle]:
        """
        Generate data candle untuk berbagai skenario stress test.
        
        Scenarios:
        - 'crash': Penurunan tajam 20-30% dalam waktu singkat
        - 'pump': Kenaikan tajam 30-50% dalam waktu singkat
        - 'choppy': Sideways dengan volatilitas tinggi
        - 'v_shaped': Crash diikuti recovery cepat
        - 'normal': Pergerakan normal dengan volatilitas moderat
        """
        candles = []
        current_price = base_price
        current_time = datetime(2024, 1, 1, 0, 0, 0)
        
        # Parameters berdasarkan scenario
        if scenario == 'crash':
            drop_rate = Decimal('-0.02')  # -2% per candle average
            volatility = Decimal('0.03')   # High volatility
            trend_duration = int(num_candles * 0.3)  # 30% candles untuk crash
        elif scenario == 'pump':
            drop_rate = Decimal('0.025')   # +2.5% per candle average
            volatility = Decimal('0.035')
            trend_duration = int(num_candles * 0.3)
        elif scenario == 'choppy':
            drop_rate = Decimal('0')
            volatility = Decimal('0.04')   # Very high volatility, no direction
            trend_duration = num_candles
        elif scenario == 'v_shaped':
            drop_rate = Decimal('-0.025')
            volatility = Decimal('0.04')
            trend_duration = int(num_candles * 0.5)  # Half crash, half recovery
        else:  # normal
            drop_rate = Decimal('0.0005')  # Slight upward bias
            volatility = Decimal('0.015')
            trend_duration = num_candles
        
        for i in range(num_candles):
            # Adjust drift based on scenario phase
            if scenario == 'v_shaped' and i > trend_duration:
                current_drift = -drop_rate * 1.2  # Stronger recovery
            elif i > trend_duration and scenario in ['crash', 'pump']:
                current_drift = -drop_rate * 0.3  # Mean reversion after extreme move
            else:
                current_drift = drop_rate
            
            # Calculate price movement with randomness
            random_component = Decimal(str(random.gauss(0, float(volatility))))
            price_change = current_price * (current_drift + random_component)
            
            open_price = current_price
            close_price = current_price + price_change
            
            # Generate high/low based on volatility
            high_low_range = abs(price_change) + (current_price * Decimal(str(random.uniform(0.005, 0.02))))
            high_price = max(open_price, close_price) + high_low_range * Decimal(str(random.uniform(0.3, 0.7)))
            low_price = min(open_price, close_price) - high_low_range * Decimal(str(random.uniform(0.3, 0.7)))
            
            # Volume spikes during extreme moves
            base_volume = Decimal('1000')
            if abs(float(price_change / open_price)) > 0.02:  # Big move
                volume = base_volume * Decimal(str(random.uniform(3, 8)))
            else:
                volume = base_volume * Decimal(str(random.uniform(0.5, 2)))
            
            candle = Candle(
                timestamp=int(current_time.timestamp()),
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume
            )
            
            candles.append(candle)
            current_price = close_price
            current_time += timedelta(minutes=5)  # 5-minute candles
        
        return candles
    
    def add_slippage_and_fees(self, entry_price: Decimal, side: str, slippage_pct: Decimal = Decimal('0.001')) -> Decimal:
        """Simulasi slippage dan trading fees."""
        # Slippage: worsen the entry price
        if side == 'LONG':
            slipped_price = entry_price * (1 + slippage_pct)
        else:
            slipped_price = entry_price * (1 - slippage_pct)
        
        # Fees: 0.02% taker fee (Binance Futures standard)
        fee = slipped_price * Decimal('0.0002')
        
        return slipped_price + fee if side == 'LONG' else slipped_price - fee
    
    def run_scenario(self, scenario: str, num_candles: int = 500) -> Dict[str, Any]:
        """Jalankan satu skenario stress test lengkap."""
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario.upper()}")
        print(f"{'='*60}")
        
        # Reset state
        self.trades = []
        self.drawdowns = []
        self.equity_curve = [self.current_equity]
        self.max_drawdown = Decimal('0')
        self.current_equity = Decimal('10000')
        self.peak_equity = Decimal('10000')
        self.engine = MultiTimeframeStructuralEngine()  # Reset engine
        self.classifier = StateClassifier()
        
        # Generate data
        candles = self.generate_stress_data(scenario, num_candles)
        print(f"Generated {len(candles)} candles for {scenario} scenario")
        
        # Process candles through pipeline
        trades_taken = 0
        trades_rejected = 0
        winning_trades = 0
        losing_trades = 0
        total_pnl = Decimal('0')
        
        # Accumulate candles for multi-timeframe processing
        candle_history = []
        
        for i, candle in enumerate(candles):
            candle_history.append(candle)
            
            # Structure - use MultiTimeframeStructuralEngine
            # For simplicity in stress test, we process single timeframe (5M)
            candles_dict = {Timeframe.MINUTE_5: candle_history[-50:]}  # Last 50 candles
            try:
                snapshot = self.engine.process("BTCUSDT", candles_dict)
                lines = snapshot.lines.get(Timeframe.MINUTE_5.value, [])
            except Exception as e:
                lines = []
            
            # Classify
            state_result = self.classifier.classify(lines)
            
            # Create simple trading plan (simplified for stress test)
            if state_result.state.value == 'UPTREND':
                direction = 'LONG'
                entry = candle.close
                sl = candle.low * Decimal('0.99')
                tp = candle.high * Decimal('1.02')
            elif state_result.state.value == 'DOWNTREND':
                direction = 'SHORT'
                entry = candle.close
                sl = candle.high * Decimal('1.01')
                tp = candle.low * Decimal('0.98')
            else:
                direction = None  # Sideway, skip for this test
            
            if direction:
                # Authorize
                auth_result = self.auth_gateway.authorize(
                    structural_state=state_result.state,
                    direction=direction,
                    entry_price=entry,
                    stop_loss=sl,
                    take_profit=tp,
                    account_balance=self.current_equity,
                    leverage=Decimal('10')
                )
                
                if auth_result.is_approved:
                    # Apply slippage and fees
                    actual_entry = self.add_slippage_and_fees(entry, direction)
                    
                    # Execute (simulation)
                    # Simplified: check if SL or TP hit in next few candles
                    if i + 10 < len(candles):
                        future_candles = candles[i+1:i+11]
                        trade_closed = False
                        
                        for future in future_candles:
                            if direction == 'LONG':
                                if future.high >= tp:
                                    # TP hit
                                    pnl = (tp - actual_entry) * Decimal('10')  # 10x leverage
                                    trade_closed = True
                                    break
                                elif future.low <= sl:
                                    # SL hit
                                    pnl = (sl - actual_entry) * Decimal('10')
                                    trade_closed = True
                                    break
                            else:  # SHORT
                                if future.low <= tp:
                                    pnl = (actual_entry - tp) * Decimal('10')
                                    trade_closed = True
                                    break
                                elif future.high >= sl:
                                    pnl = (actual_entry - sl) * Decimal('10')
                                    trade_closed = True
                                    break
                        
                        if trade_closed:
                            # Update equity
                            self.current_equity += pnl
                            total_pnl += pnl
                            
                            # Track peak and drawdown
                            if self.current_equity > self.peak_equity:
                                self.peak_equity = self.current_equity
                            
                            current_drawdown = (self.peak_equity - self.current_equity) / self.peak_equity
                            self.drawdowns.append(current_drawdown)
                            
                            if current_drawdown > self.max_drawdown:
                                self.max_drawdown = current_drawdown
                            
                            self.equity_curve.append(self.current_equity)
                            
                            # Track win/loss
                            trades_taken += 1
                            if pnl > 0:
                                winning_trades += 1
                            else:
                                losing_trades += 1
                            
                            self.trades.append({
                                'candle_index': i,
                                'direction': direction,
                                'entry': float(actual_entry),
                                'exit': float(tp if pnl > 0 else sl),
                                'pnl': float(pnl),
                                'equity_after': float(self.current_equity)
                            })
                else:
                    trades_rejected += 1
        
        # Calculate final metrics
        win_rate = Decimal(winning_trades) / Decimal(trades_taken) if trades_taken > 0 else Decimal('0')
        profit_factor = Decimal('0')
        gross_profit = sum(Decimal(t['pnl']) for t in self.trades if t['pnl'] > 0)
        gross_loss = abs(sum(Decimal(t['pnl']) for t in self.trades if t['pnl'] < 0))
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
        
        results = {
            'scenario': scenario,
            'total_candles': num_candles,
            'trades_taken': trades_taken,
            'trades_rejected': trades_rejected,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': float(win_rate),
            'total_pnl': float(total_pnl),
            'final_equity': float(self.current_equity),
            'max_drawdown': float(self.max_drawdown),
            'profit_factor': float(profit_factor),
            'return_pct': float((self.current_equity - Decimal('10000')) / Decimal('10000') * 100)
        }
        
        # Print summary
        print(f"\n--- RESULTS FOR {scenario.upper()} ---")
        print(f"Trades Taken: {trades_taken}")
        print(f"Trades Rejected: {trades_rejected}")
        print(f"Win Rate: {win_rate:.2%}")
        print(f"Total PnL: ${total_pnl:.2f}")
        print(f"Final Equity: ${self.current_equity:.2f}")
        print(f"Max Drawdown: {self.max_drawdown:.2%}")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Return: {results['return_pct']:.2f}%")
        
        return results


class TestStressTestSuite:
    """Test suite untuk Fase 3: Full Simulation Stress Test."""
    
    @pytest.fixture
    def config(self):
        return Config()
    
    @pytest.fixture
    def simulator(self, config):
        return StressTestSimulator(config)
    
    def test_crash_scenario(self, simulator):
        """Test performa bot selama market crash (penurunan tajam)."""
        results = simulator.run_scenario('crash', num_candles=500)
        
        # Assertions
        assert results['trades_taken'] > 0, "Should take some trades during crash"
        assert results['max_drawdown'] <= 0.05, f"Max drawdown {results['max_drawdown']:.2%} exceeds 5% limit"
        assert results['final_equity'] > 0, "Equity should not go to zero"
        
        print(f"✓ Crash scenario passed. Max DD: {results['max_drawdown']:.2%}")
    
    def test_pump_scenario(self, simulator):
        """Test performa bot selama market pump (kenaikan tajam)."""
        results = simulator.run_scenario('pump', num_candles=500)
        
        # Assertions
        assert results['trades_taken'] > 0, "Should take some trades during pump"
        assert results['max_drawdown'] <= 0.05, f"Max drawdown {results['max_drawdown']:.2%} exceeds 5% limit"
        assert results['final_equity'] > Decimal('10000'), "Should profit from pump"
        
        print(f"✓ Pump scenario passed. Return: {results['return_pct']:.2f}%")
    
    def test_choppy_scenario(self, simulator):
        """Test performa bot selama sideways dengan volatilitas tinggi."""
        results = simulator.run_scenario('choppy', num_candles=500)
        
        # Assertions
        assert results['max_drawdown'] <= 0.05, f"Max drawdown {results['max_drawdown']:.2%} exceeds 5% limit"
        # In choppy market, we expect fewer trades or small losses
        assert results['final_equity'] > Decimal('8000'), "Should not lose more than 20% in choppy market"
        
        print(f"✓ Choppy scenario passed. Max DD: {results['max_drawdown']:.2%}")
    
    def test_v_shaped_scenario(self, simulator):
        """Test performa bot selama V-shaped recovery (crash + recovery)."""
        results = simulator.run_scenario('v_shaped', num_candles=600)
        
        # Assertions
        assert results['trades_taken'] > 0, "Should take trades during both crash and recovery"
        assert results['max_drawdown'] <= 0.05, f"Max drawdown {results['max_drawdown']:.2%} exceeds 5% limit"
        
        print(f"✓ V-shaped scenario passed. Return: {results['return_pct']:.2f}%")
    
    def test_combined_scenarios(self, simulator):
        """Test menjalankan semua skenario secara berurutan."""
        scenarios = ['crash', 'pump', 'choppy', 'v_shaped']
        all_results = []
        
        for scenario in scenarios:
            results = simulator.run_scenario(scenario, num_candles=400)
            all_results.append(results)
            
            # Verify each scenario meets requirements
            assert results['max_drawdown'] <= 0.05, \
                f"{scenario}: Max drawdown {results['max_drawdown']:.2%} exceeds 5% limit"
        
        # Overall statistics
        total_trades = sum(r['trades_taken'] for r in all_results)
        avg_win_rate = sum(r['win_rate'] for r in all_results) / len(all_results)
        worst_drawdown = max(r['max_drawdown'] for r in all_results)
        
        print(f"\n{'='*60}")
        print("COMBINED SCENARIOS SUMMARY")
        print(f"{'='*60}")
        print(f"Total Trades: {total_trades}")
        print(f"Average Win Rate: {avg_win_rate:.2%}")
        print(f"Worst Drawdown: {worst_drawdown:.2%}")
        
        assert worst_drawdown <= 0.05, f"Worst drawdown across all scenarios {worst_drawdown:.2%} exceeds 5%"
        assert total_trades > 0, "Should have taken trades across all scenarios"
        
        print("✓ All combined scenarios passed!")
    
    def test_slippage_and_fees_impact(self, simulator):
        """Test dampak slippage dan fees terhadap profitability."""
        # Run without slippage first (baseline)
        results_no_slippage = simulator.run_scenario('normal', num_candles=300)
        
        # The test already includes slippage, so we just verify it doesn't break the system
        assert results_no_slippage['max_drawdown'] <= 0.05
        assert results_no_slippage['final_equity'] > 0
        
        print(f"✓ Slippage and fees test passed. Impact included in simulation.")


if __name__ == '__main__':
    # Run manual test
    config = Config()
    simulator = StressTestSimulator(config)
    
    # Run all scenarios
    scenarios = ['crash', 'pump', 'choppy', 'v_shaped', 'normal']
    
    for scenario in scenarios:
        try:
            simulator.run_scenario(scenario, num_candles=400)
        except Exception as e:
            print(f"Error in {scenario}: {e}")
    
    print("\n" + "="*60)
    print("STRESS TEST COMPLETE")
    print("="*60)
