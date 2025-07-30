"""
ROI Calculator for Business Value Quantification

Advanced ROI analysis system that quantifies the business impact and return on investment
of productivity tools, configurations, and workflow optimizations with financial modeling.
"""

import json
import math
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from enum import Enum
import logging
import statistics
from collections import defaultdict
import sqlite3

from .metrics_collector import MetricsCollector, MetricType, MetricPoint

class ROIMetricType(Enum):
    """Types of ROI metrics calculated"""
    TIME_SAVINGS = "time_savings"
    PRODUCTIVITY_GAIN = "productivity_gain" 
    ERROR_REDUCTION = "error_reduction"
    COST_AVOIDANCE = "cost_avoidance"
    EFFICIENCY_IMPROVEMENT = "efficiency_improvement"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    TRAINING_REDUCTION = "training_reduction"
    MAINTENANCE_SAVINGS = "maintenance_savings"

class CostType(Enum):
    """Types of costs tracked"""
    IMPLEMENTATION = "implementation"
    TRAINING = "training"
    MAINTENANCE = "maintenance"
    LICENSING = "licensing"
    INFRASTRUCTURE = "infrastructure"
    OPPORTUNITY = "opportunity"

class BenefitType(Enum):
    """Types of benefits tracked"""
    DIRECT_SAVINGS = "direct_savings"
    PRODUCTIVITY_GAINS = "productivity_gains"
    QUALITY_IMPROVEMENTS = "quality_improvements"
    RISK_REDUCTION = "risk_reduction"
    SCALABILITY_BENEFITS = "scalability_benefits"
    INNOVATION_ACCELERATION = "innovation_acceleration"

@dataclass
class ROIBenchmark:
    """Industry benchmarks for ROI calculations"""
    industry: str
    role: str
    hourly_rate: float
    productivity_baseline: float
    error_cost_factor: float
    quality_value_multiplier: float

@dataclass
class CostItem:
    """Individual cost component"""
    cost_id: str
    name: str 
    cost_type: CostType
    amount: float
    frequency: str  # one_time, monthly, annually
    start_date: datetime
    end_date: Optional[datetime] = None
    description: str = ""
    allocated_percentage: float = 100.0  # % allocated to this ROI calculation

@dataclass
class BenefitItem:
    """Individual benefit component"""
    benefit_id: str
    name: str
    benefit_type: BenefitType
    amount: float
    frequency: str  # one_time, monthly, annually
    start_date: datetime
    end_date: Optional[datetime] = None
    confidence: float = 0.8  # Confidence level (0-1)
    realization_curve: str = "linear"  # linear, exponential, s_curve
    description: str = ""

@dataclass
class ROIScenario:
    """ROI calculation scenario"""
    scenario_id: str
    name: str
    description: str
    costs: List[CostItem]
    benefits: List[BenefitItem]
    analysis_period_months: int = 36
    discount_rate: float = 0.08  # Annual discount rate
    risk_factor: float = 0.1  # Risk adjustment factor

@dataclass
class ROIResult:
    """Comprehensive ROI calculation result"""
    scenario_id: str
    calculation_date: datetime
    analysis_period_months: int
    
    # Financial metrics
    total_costs: float
    total_benefits: float
    net_present_value: float
    roi_percentage: float
    payback_period_months: float
    internal_rate_of_return: float
    
    # Benefit-cost analysis
    benefit_cost_ratio: float
    break_even_point: datetime
    
    # Risk analysis
    sensitivity_analysis: Dict[str, float]
    confidence_interval: Tuple[float, float]  # (low, high) ROI estimates
    
    # Detailed breakdowns
    cost_breakdown: Dict[str, float]
    benefit_breakdown: Dict[str, float]
    monthly_cash_flow: List[Dict[str, Any]]
    
    # Business impact metrics
    productivity_improvement: float
    time_savings_hours: float
    error_reduction_percentage: float
    quality_score_improvement: float

class ROICalculator:
    """Advanced ROI calculation and business value analysis engine"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 db_path: str = "~/.claude/eipas-system/analytics/roi.db"):
        self.logger = logging.getLogger(__name__)
        
        # Initialize metrics collector
        if metrics_collector:
            self.metrics_collector = metrics_collector
        else:
            self.metrics_collector = MetricsCollector()
        
        # Database setup
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize benchmarks and models
        self.benchmarks = self._init_industry_benchmarks()
        self.cost_models = self._init_cost_models()
        self.benefit_models = self._init_benefit_models()
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize ROI database schema"""
        with sqlite3.connect(str(self.db_path)) as conn:
            # ROI scenarios table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS roi_scenarios (
                    scenario_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    analysis_period_months INTEGER,
                    discount_rate REAL,
                    risk_factor REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # ROI results table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS roi_results (
                    result_id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    calculation_date TEXT NOT NULL,
                    roi_percentage REAL,
                    npv REAL,
                    payback_months REAL,
                    total_costs REAL,
                    total_benefits REAL,
                    confidence_low REAL,
                    confidence_high REAL,
                    results_json TEXT,
                    FOREIGN KEY (scenario_id) REFERENCES roi_scenarios (scenario_id)
                )
            """)
            
            # Cost items table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cost_items (
                    cost_id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    cost_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    frequency TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    allocated_percentage REAL DEFAULT 100.0,
                    FOREIGN KEY (scenario_id) REFERENCES roi_scenarios (scenario_id)
                )
            """)
            
            # Benefit items table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benefit_items (
                    benefit_id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    benefit_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    frequency TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    confidence REAL DEFAULT 0.8,
                    realization_curve TEXT DEFAULT 'linear',
                    FOREIGN KEY (scenario_id) REFERENCES roi_scenarios (scenario_id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_roi_results_scenario ON roi_results(scenario_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_roi_results_date ON roi_results(calculation_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_costs_scenario ON cost_items(scenario_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benefits_scenario ON benefit_items(scenario_id)")
    
    def _init_industry_benchmarks(self) -> Dict[str, ROIBenchmark]:
        """Initialize industry and role benchmarks"""
        return {
            'software_engineer': ROIBenchmark(
                industry='technology',
                role='software_engineer',
                hourly_rate=85.0,
                productivity_baseline=100.0,
                error_cost_factor=2.5,
                quality_value_multiplier=1.8
            ),
            'senior_engineer': ROIBenchmark(
                industry='technology',
                role='senior_engineer', 
                hourly_rate=120.0,
                productivity_baseline=120.0,
                error_cost_factor=3.2,
                quality_value_multiplier=2.1
            ),
            'data_scientist': ROIBenchmark(
                industry='technology',
                role='data_scientist',
                hourly_rate=95.0,
                productivity_baseline=110.0,
                error_cost_factor=2.8,
                quality_value_multiplier=2.0
            ),
            'product_manager': ROIBenchmark(
                industry='technology',
                role='product_manager',
                hourly_rate=105.0,
                productivity_baseline=95.0,
                error_cost_factor=2.2,
                quality_value_multiplier=1.9
            ),
            'devops_engineer': ROIBenchmark(
                industry='technology',
                role='devops_engineer',
                hourly_rate=100.0,
                productivity_baseline=115.0,
                error_cost_factor=3.5,
                quality_value_multiplier=2.3
            )
        }
    
    def _init_cost_models(self) -> Dict[str, Dict]:
        """Initialize cost calculation models"""
        return {
            'claude_code_implementation': {
                'setup_hours': 8,
                'training_hours_per_user': 4,
                'maintenance_hours_monthly': 2,
                'license_cost_monthly': 20.0,
                'infrastructure_cost_monthly': 5.0
            },
            'workflow_optimization': {
                'analysis_hours': 16,
                'implementation_hours': 24,
                'testing_hours': 8,
                'rollout_hours': 12,
                'change_management_hours': 20
            },
            'tool_integration': {
                'research_hours': 6,
                'development_hours': 32,
                'testing_hours': 12,
                'documentation_hours': 8,
                'training_hours': 16
            }
        }
    
    def _init_benefit_models(self) -> Dict[str, Dict]:
        """Initialize benefit calculation models"""
        return {
            'productivity_gains': {
                'time_savings_percentage': 0.15,  # 15% average time savings
                'quality_improvement_factor': 1.25,
                'error_reduction_percentage': 0.30,
                'ramp_up_months': 3
            },
            'automation_benefits': {
                'manual_task_reduction': 0.40,  # 40% reduction in manual tasks
                'consistency_improvement': 0.85,
                'scalability_factor': 2.0,
                'maintenance_reduction': 0.25
            },
            'collaboration_improvements': {
                'communication_efficiency': 0.20,
                'knowledge_sharing_value': 0.18,
                'onboarding_speed_improvement': 0.35,
                'decision_making_speed': 0.25
            }
        }
    
    def create_scenario(self, name: str, description: str = "",
                       analysis_period_months: int = 36,
                       discount_rate: float = 0.08,
                       risk_factor: float = 0.1) -> str:
        """Create a new ROI analysis scenario"""
        
        scenario_id = f"roi_scenario_{int(datetime.now().timestamp())}"
        
        scenario = ROIScenario(
            scenario_id=scenario_id,
            name=name,
            description=description,
            costs=[],
            benefits=[],
            analysis_period_months=analysis_period_months,
            discount_rate=discount_rate,
            risk_factor=risk_factor
        )
        
        # Store in database
        self._store_scenario(scenario)
        
        self.logger.info(f"Created ROI scenario: {scenario_id}")
        return scenario_id
    
    def add_cost_item(self, scenario_id: str, name: str, cost_type: CostType,
                     amount: float, frequency: str = "one_time",
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     allocated_percentage: float = 100.0,
                     description: str = "") -> str:
        """Add a cost item to scenario"""
        
        if start_date is None:
            start_date = datetime.now(timezone.utc)
        
        cost_id = f"cost_{int(datetime.now().timestamp())}"
        
        cost_item = CostItem(
            cost_id=cost_id,
            name=name,
            cost_type=cost_type,
            amount=amount,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            description=description,
            allocated_percentage=allocated_percentage
        )
        
        # Store in database
        self._store_cost_item(scenario_id, cost_item)
        
        self.logger.info(f"Added cost item {cost_id} to scenario {scenario_id}")
        return cost_id
    
    def add_benefit_item(self, scenario_id: str, name: str, benefit_type: BenefitType,
                        amount: float, frequency: str = "monthly",
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        confidence: float = 0.8,
                        realization_curve: str = "linear",
                        description: str = "") -> str:
        """Add a benefit item to scenario"""
        
        if start_date is None:
            start_date = datetime.now(timezone.utc)
        
        benefit_id = f"benefit_{int(datetime.now().timestamp())}"
        
        benefit_item = BenefitItem(
            benefit_id=benefit_id,
            name=name,
            benefit_type=benefit_type,
            amount=amount,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            confidence=confidence,
            realization_curve=realization_curve,
            description=description
        )
        
        # Store in database
        self._store_benefit_item(scenario_id, benefit_item)
        
        self.logger.info(f"Added benefit item {benefit_id} to scenario {scenario_id}")
        return benefit_id
    
    def calculate_roi(self, scenario_id: str, benchmark_role: str = "software_engineer") -> ROIResult:
        """Calculate comprehensive ROI for scenario"""
        
        try:
            # Load scenario data
            scenario = self._load_scenario(scenario_id)
            costs = self._load_cost_items(scenario_id)
            benefits = self._load_benefit_items(scenario_id)
            
            if not scenario:
                raise ValueError(f"Scenario {scenario_id} not found")
            
            # Get benchmark data
            benchmark = self.benchmarks.get(benchmark_role, self.benchmarks['software_engineer'])
            
            # Calculate monthly cash flows
            monthly_cash_flow = self._calculate_monthly_cash_flow(
                costs, benefits, scenario.analysis_period_months, scenario.discount_rate
            )
            
            # Calculate financial metrics
            total_costs = sum(cf['costs'] for cf in monthly_cash_flow)
            total_benefits = sum(cf['benefits'] for cf in monthly_cash_flow)
            
            net_present_value = sum(cf['net_cash_flow_pv'] for cf in monthly_cash_flow)
            roi_percentage = ((total_benefits - total_costs) / total_costs * 100) if total_costs > 0 else 0
            
            # Calculate payback period
            payback_period = self._calculate_payback_period(monthly_cash_flow)
            
            # Calculate IRR (simplified)
            irr = self._calculate_irr(monthly_cash_flow)
            
            # Calculate benefit-cost ratio
            bcr = total_benefits / total_costs if total_costs > 0 else 0
            
            # Calculate break-even point
            break_even_point = self._calculate_break_even_point(monthly_cash_flow)
            
            # Perform sensitivity analysis
            sensitivity = self._perform_sensitivity_analysis(scenario_id, costs, benefits, scenario)
            
            # Calculate confidence intervals
            confidence_interval = self._calculate_confidence_intervals(
                roi_percentage, benefits, scenario.risk_factor
            )
            
            # Calculate business impact metrics
            business_impact = self._calculate_business_impact(benefits, benchmark)
            
            # Create result
            result = ROIResult(
                scenario_id=scenario_id,
                calculation_date=datetime.now(timezone.utc),
                analysis_period_months=scenario.analysis_period_months,
                total_costs=total_costs,
                total_benefits=total_benefits,
                net_present_value=net_present_value,
                roi_percentage=roi_percentage,
                payback_period_months=payback_period,
                internal_rate_of_return=irr,
                benefit_cost_ratio=bcr,
                break_even_point=break_even_point,
                sensitivity_analysis=sensitivity,
                confidence_interval=confidence_interval,
                cost_breakdown=self._calculate_cost_breakdown(costs),
                benefit_breakdown=self._calculate_benefit_breakdown(benefits),
                monthly_cash_flow=monthly_cash_flow,
                productivity_improvement=business_impact['productivity_improvement'],
                time_savings_hours=business_impact['time_savings_hours'],
                error_reduction_percentage=business_impact['error_reduction_percentage'],
                quality_score_improvement=business_impact['quality_score_improvement']
            )
            
            # Store result
            self._store_roi_result(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating ROI for scenario {scenario_id}: {e}")
            raise
    
    def create_productivity_roi_scenario(self, user_count: int = 10,
                                       benchmark_role: str = "software_engineer",
                                       productivity_improvement: float = 0.15) -> str:
        """Create a pre-configured productivity improvement ROI scenario"""
        
        scenario_id = self.create_scenario(
            name=f"Claude Code Productivity ROI - {user_count} Users",
            description=f"ROI analysis for Claude Code implementation with {productivity_improvement*100}% productivity improvement",
            analysis_period_months=36
        )
        
        benchmark = self.benchmarks.get(benchmark_role, self.benchmarks['software_engineer'])
        
        # Implementation costs
        self.add_cost_item(
            scenario_id=scenario_id,
            name="Initial Setup and Configuration",
            cost_type=CostType.IMPLEMENTATION,
            amount=benchmark.hourly_rate * 16,  # 16 hours setup
            frequency="one_time",
            description="Initial Claude Code setup, configuration, and customization"
        )
        
        self.add_cost_item(
            scenario_id=scenario_id,
            name="User Training",
            cost_type=CostType.TRAINING,
            amount=benchmark.hourly_rate * 4 * user_count,  # 4 hours per user
            frequency="one_time",
            description="Training users on Claude Code features and best practices"
        )
        
        self.add_cost_item(
            scenario_id=scenario_id,
            name="Monthly Maintenance",
            cost_type=CostType.MAINTENANCE,
            amount=benchmark.hourly_rate * 4,  # 4 hours monthly
            frequency="monthly",
            description="Ongoing maintenance, updates, and support"
        )
        
        self.add_cost_item(
            scenario_id=scenario_id,
            name="Licensing Costs",
            cost_type=CostType.LICENSING,
            amount=20.0 * user_count,  # $20 per user per month
            frequency="monthly",
            description="Claude Code licensing and subscription costs"
        )
        
        # Productivity benefits
        monthly_work_hours = 160  # Standard full-time hours
        hours_saved_per_user = monthly_work_hours * productivity_improvement
        monthly_savings = hours_saved_per_user * benchmark.hourly_rate * user_count
        
        self.add_benefit_item(
            scenario_id=scenario_id,
            name="Productivity Time Savings",
            benefit_type=BenefitType.PRODUCTIVITY_GAINS,
            amount=monthly_savings,
            frequency="monthly",
            confidence=0.85,
            realization_curve="s_curve",
            description=f"Time savings from {productivity_improvement*100}% productivity improvement"
        )
        
        # Quality improvements
        quality_value = benchmark.hourly_rate * benchmark.quality_value_multiplier * user_count * 0.5
        self.add_benefit_item(
            scenario_id=scenario_id,
            name="Code Quality Improvements",
            benefit_type=BenefitType.QUALITY_IMPROVEMENTS,
            amount=quality_value,
            frequency="monthly",
            confidence=0.75,
            description="Value from improved code quality and reduced technical debt"
        )
        
        # Error reduction
        error_reduction_value = benchmark.hourly_rate * benchmark.error_cost_factor * user_count * 0.3
        self.add_benefit_item(
            scenario_id=scenario_id,
            name="Error Reduction Savings",
            benefit_type=BenefitType.RISK_REDUCTION,
            amount=error_reduction_value,
            frequency="monthly",
            confidence=0.80,
            description="Savings from reduced errors and debugging time"
        )
        
        return scenario_id
    
    def _calculate_monthly_cash_flow(self, costs: List[CostItem], benefits: List[BenefitItem],
                                   analysis_months: int, discount_rate: float) -> List[Dict[str, Any]]:
        """Calculate monthly cash flow projections"""
        
        monthly_discount_rate = discount_rate / 12
        cash_flow = []
        
        for month in range(analysis_months):
            month_date = datetime.now() + timedelta(days=30 * month)
            
            # Calculate costs for this month
            monthly_costs = 0.0
            for cost in costs:
                cost_amount = self._get_monthly_cost_amount(cost, month, month_date)
                monthly_costs += cost_amount
            
            # Calculate benefits for this month
            monthly_benefits = 0.0
            for benefit in benefits:
                benefit_amount = self._get_monthly_benefit_amount(benefit, month, month_date)
                monthly_benefits += benefit_amount
            
            # Calculate net cash flow and present value
            net_cash_flow = monthly_benefits - monthly_costs
            present_value_factor = (1 + monthly_discount_rate) ** month
            net_cash_flow_pv = net_cash_flow / present_value_factor
            
            cash_flow.append({
                'month': month + 1,
                'date': month_date.strftime('%Y-%m-%d'),
                'costs': monthly_costs,
                'benefits': monthly_benefits,
                'net_cash_flow': net_cash_flow,
                'net_cash_flow_pv': net_cash_flow_pv,
                'cumulative_cash_flow': sum(cf.get('net_cash_flow', 0) for cf in cash_flow) + net_cash_flow
            })
        
        return cash_flow
    
    def _get_monthly_cost_amount(self, cost: CostItem, month: int, month_date: datetime) -> float:
        """Calculate cost amount for specific month"""
        
        # Check if cost is active in this month
        if month_date < cost.start_date:
            return 0.0
        
        if cost.end_date and month_date > cost.end_date:
            return 0.0
        
        allocated_amount = cost.amount * (cost.allocated_percentage / 100.0)
        
        if cost.frequency == "one_time":
            return allocated_amount if month == 0 else 0.0
        elif cost.frequency == "monthly":
            return allocated_amount
        elif cost.frequency == "annually":
            return allocated_amount / 12
        elif cost.frequency == "quarterly":
            return allocated_amount / 3 if month % 3 == 0 else 0.0
        
        return 0.0
    
    def _get_monthly_benefit_amount(self, benefit: BenefitItem, month: int, month_date: datetime) -> float:
        """Calculate benefit amount for specific month with realization curves"""
        
        # Check if benefit is active in this month
        if month_date < benefit.start_date:
            return 0.0
        
        if benefit.end_date and month_date > benefit.end_date:
            return 0.0
        
        base_amount = benefit.amount * benefit.confidence
        
        # Apply frequency
        if benefit.frequency == "one_time":
            monthly_amount = base_amount if month == 0 else 0.0
        elif benefit.frequency == "monthly":
            monthly_amount = base_amount
        elif benefit.frequency == "annually":
            monthly_amount = base_amount / 12
        elif benefit.frequency == "quarterly":
            monthly_amount = base_amount / 3 if month % 3 == 0 else 0.0
        else:
            monthly_amount = base_amount
        
        # Apply realization curve
        if benefit.realization_curve == "linear":
            return monthly_amount
        elif benefit.realization_curve == "s_curve":
            # S-curve: slow start, accelerated middle, plateau
            progress = min(1.0, month / 12.0)  # 12-month ramp
            curve_factor = 1 / (1 + math.exp(-6 * (progress - 0.5)))
            return monthly_amount * curve_factor
        elif benefit.realization_curve == "exponential":
            # Exponential growth
            curve_factor = min(1.0, 0.2 * (1.5 ** month))
            return monthly_amount * curve_factor
        
        return monthly_amount
    
    def _calculate_payback_period(self, cash_flow: List[Dict[str, Any]]) -> float:
        """Calculate payback period in months"""
        
        cumulative_cash_flow = 0.0
        
        for i, cf in enumerate(cash_flow):
            cumulative_cash_flow += cf['net_cash_flow']
            
            if cumulative_cash_flow >= 0:
                # Interpolate for exact payback time
                if i == 0:
                    return 1.0
                
                prev_cumulative = cumulative_cash_flow - cf['net_cash_flow']
                fraction = abs(prev_cumulative) / cf['net_cash_flow']
                return i + fraction
        
        return len(cash_flow)  # Payback beyond analysis period
    
    def _calculate_irr(self, cash_flow: List[Dict[str, Any]]) -> float:
        """Calculate Internal Rate of Return (simplified)"""
        
        # Simplified IRR calculation using binary search
        flows = [cf['net_cash_flow'] for cf in cash_flow]
        
        if not flows or all(f <= 0 for f in flows):
            return 0.0
        
        # Binary search for IRR
        low, high = -0.5, 2.0
        
        for _ in range(100):  # Max iterations
            mid = (low + high) / 2
            npv = sum(flow / ((1 + mid/12) ** (i + 1)) for i, flow in enumerate(flows))
            
            if abs(npv) < 0.01:
                return mid * 12  # Convert to annual rate
            
            if npv > 0:
                low = mid
            else:
                high = mid
        
        return 0.15  # Default 15% if no convergence
    
    def _calculate_break_even_point(self, cash_flow: List[Dict[str, Any]]) -> datetime:
        """Calculate break-even point date"""
        
        for cf in cash_flow:
            if cf['cumulative_cash_flow'] >= 0:
                return datetime.strptime(cf['date'], '%Y-%m-%d')
        
        # If no break-even in analysis period
        last_date = datetime.strptime(cash_flow[-1]['date'], '%Y-%m-%d')
        return last_date + timedelta(days=365)  # Estimate 1 year beyond
    
    def _perform_sensitivity_analysis(self, scenario_id: str, costs: List[CostItem],
                                    benefits: List[BenefitItem], scenario: ROIScenario) -> Dict[str, float]:
        """Perform sensitivity analysis on key variables"""
        
        base_roi = self.calculate_roi(scenario_id).roi_percentage
        sensitivity = {}
        
        # Test cost variations (+/- 20%)
        for variation in [-0.2, 0.2]:
            modified_costs = []
            for cost in costs:
                modified_cost = CostItem(
                    cost_id=cost.cost_id,
                    name=cost.name,
                    cost_type=cost.cost_type,
                    amount=cost.amount * (1 + variation),
                    frequency=cost.frequency,
                    start_date=cost.start_date,
                    end_date=cost.end_date
                )
                modified_costs.append(modified_cost)
            
            cash_flow = self._calculate_monthly_cash_flow(
                modified_costs, benefits, scenario.analysis_period_months, scenario.discount_rate
            )
            
            total_costs = sum(cf['costs'] for cf in cash_flow)
            total_benefits = sum(cf['benefits'] for cf in cash_flow)
            roi = ((total_benefits - total_costs) / total_costs * 100) if total_costs > 0 else 0
            
            sensitivity[f'cost_variation{int(variation*100):+d}%'] = roi - base_roi
        
        # Test benefit variations (+/- 20%)
        for variation in [-0.2, 0.2]:
            modified_benefits = []
            for benefit in benefits:
                modified_benefit = BenefitItem(
                    benefit_id=benefit.benefit_id,
                    name=benefit.name,
                    benefit_type=benefit.benefit_type,
                    amount=benefit.amount * (1 + variation),
                    frequency=benefit.frequency,
                    start_date=benefit.start_date,
                    end_date=benefit.end_date,
                    confidence=benefit.confidence
                )
                modified_benefits.append(modified_benefit)
            
            cash_flow = self._calculate_monthly_cash_flow(
                costs, modified_benefits, scenario.analysis_period_months, scenario.discount_rate
            )
            
            total_costs = sum(cf['costs'] for cf in cash_flow)
            total_benefits = sum(cf['benefits'] for cf in cash_flow)
            roi = ((total_benefits - total_costs) / total_costs * 100) if total_costs > 0 else 0
            
            sensitivity[f'benefit_variation{int(variation*100):+d}%'] = roi - base_roi
        
        return sensitivity
    
    def _calculate_confidence_intervals(self, base_roi: float, benefits: List[BenefitItem],
                                      risk_factor: float) -> Tuple[float, float]:
        """Calculate confidence intervals for ROI estimate"""
        
        # Calculate confidence based on benefit confidence levels and risk factor
        weighted_confidence = sum(b.confidence * b.amount for b in benefits) / sum(b.amount for b in benefits) if benefits else 0.8
        
        # Adjust for risk factor
        confidence_adjustment = (1 - risk_factor) * weighted_confidence
        
        # Calculate range (+/- based on confidence)
        uncertainty_range = base_roi * (1 - confidence_adjustment) * 0.3  # 30% of uncertainty
        
        return (base_roi - uncertainty_range, base_roi + uncertainty_range)
    
    def _calculate_business_impact(self, benefits: List[BenefitItem], benchmark: ROIBenchmark) -> Dict[str, float]:
        """Calculate business impact metrics"""
        
        # Aggregate benefits by type
        productivity_benefits = sum(b.amount for b in benefits 
                                   if b.benefit_type == BenefitType.PRODUCTIVITY_GAINS)
        
        quality_benefits = sum(b.amount for b in benefits 
                              if b.benefit_type == BenefitType.QUALITY_IMPROVEMENTS)
        
        risk_benefits = sum(b.amount for b in benefits 
                           if b.benefit_type == BenefitType.RISK_REDUCTION)
        
        # Calculate impact metrics
        annual_productivity_benefit = productivity_benefits * 12
        time_savings_hours = annual_productivity_benefit / benchmark.hourly_rate
        productivity_improvement = (time_savings_hours / (40 * 52)) * 100  # % of work year
        
        error_reduction_percentage = (risk_benefits * 12) / (benchmark.hourly_rate * benchmark.error_cost_factor) * 100
        quality_score_improvement = (quality_benefits * 12) / (benchmark.hourly_rate * benchmark.quality_value_multiplier) * 100
        
        return {
            'productivity_improvement': min(50.0, productivity_improvement),  # Cap at 50%
            'time_savings_hours': time_savings_hours,
            'error_reduction_percentage': min(80.0, error_reduction_percentage),  # Cap at 80%
            'quality_score_improvement': min(100.0, quality_score_improvement)  # Cap at 100%
        }
    
    def _calculate_cost_breakdown(self, costs: List[CostItem]) -> Dict[str, float]:
        """Calculate cost breakdown by type"""
        
        breakdown = defaultdict(float)
        
        for cost in costs:
            # Annualize costs for comparison
            if cost.frequency == "one_time":
                annual_amount = cost.amount
            elif cost.frequency == "monthly":
                annual_amount = cost.amount * 12
            elif cost.frequency == "annually":
                annual_amount = cost.amount
            elif cost.frequency == "quarterly":
                annual_amount = cost.amount * 4
            else:
                annual_amount = cost.amount
            
            breakdown[cost.cost_type.value] += annual_amount * (cost.allocated_percentage / 100.0)
        
        return dict(breakdown)
    
    def _calculate_benefit_breakdown(self, benefits: List[BenefitItem]) -> Dict[str, float]:
        """Calculate benefit breakdown by type"""
        
        breakdown = defaultdict(float)
        
        for benefit in benefits:
            # Annualize benefits for comparison
            if benefit.frequency == "one_time":
                annual_amount = benefit.amount
            elif benefit.frequency == "monthly":
                annual_amount = benefit.amount * 12
            elif benefit.frequency == "annually":
                annual_amount = benefit.amount
            elif benefit.frequency == "quarterly":
                annual_amount = benefit.amount * 4
            else:
                annual_amount = benefit.amount
            
            breakdown[benefit.benefit_type.value] += annual_amount * benefit.confidence
        
        return dict(breakdown)
    
    def generate_roi_report(self, result: ROIResult) -> str:
        """Generate comprehensive ROI report"""
        
        report = f"""
# ROI Analysis Report

**Scenario ID**: {result.scenario_id}
**Analysis Date**: {result.calculation_date.strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Period**: {result.analysis_period_months} months

## Executive Summary

- **Return on Investment**: {result.roi_percentage:.1f}%
- **Net Present Value**: ${result.net_present_value:,.2f}
- **Payback Period**: {result.payback_period_months:.1f} months
- **Benefit-Cost Ratio**: {result.benefit_cost_ratio:.2f}:1
- **Break-Even Date**: {result.break_even_point.strftime('%Y-%m-%d')}

## Financial Analysis

### Investment Overview
- **Total Investment**: ${result.total_costs:,.2f}
- **Total Benefits**: ${result.total_benefits:,.2f}
- **Net Benefit**: ${result.total_benefits - result.total_costs:,.2f}

### Cost Breakdown
"""
        
        for cost_type, amount in result.cost_breakdown.items():
            percentage = (amount / result.total_costs * 100) if result.total_costs > 0 else 0
            report += f"- **{cost_type.replace('_', ' ').title()}**: ${amount:,.2f} ({percentage:.1f}%)\n"
        
        report += "\n### Benefit Breakdown\n"
        
        for benefit_type, amount in result.benefit_breakdown.items():
            percentage = (amount / result.total_benefits * 100) if result.total_benefits > 0 else 0
            report += f"- **{benefit_type.replace('_', ' ').title()}**: ${amount:,.2f} ({percentage:.1f}%)\n"
        
        report += f"""

## Business Impact

- **Productivity Improvement**: {result.productivity_improvement:.1f}%
- **Time Savings**: {result.time_savings_hours:,.0f} hours annually
- **Error Reduction**: {result.error_reduction_percentage:.1f}%
- **Quality Score Improvement**: {result.quality_score_improvement:.1f}%

## Risk Analysis

### Confidence Interval
- **Conservative Estimate**: {result.confidence_interval[0]:.1f}% ROI
- **Optimistic Estimate**: {result.confidence_interval[1]:.1f}% ROI

### Sensitivity Analysis
"""
        
        for variable, impact in result.sensitivity_analysis.items():
            report += f"- **{variable}**: {impact:+.1f}% ROI impact\n"
        
        report += f"""

## Financial Metrics

- **Internal Rate of Return**: {result.internal_rate_of_return:.1f}%
- **Net Present Value**: ${result.net_present_value:,.2f}
- **Payback Period**: {result.payback_period_months:.1f} months
- **Benefit-Cost Ratio**: {result.benefit_cost_ratio:.2f}

## Recommendation

"""
        
        if result.roi_percentage > 25:
            report += "**STRONG RECOMMENDATION**: This investment shows excellent returns with low risk."
        elif result.roi_percentage > 15:
            report += "**RECOMMENDED**: This investment provides good returns above market rates."
        elif result.roi_percentage > 5:
            report += "**CONDITIONAL**: Consider if strategic benefits justify modest returns."
        else:
            report += "**NOT RECOMMENDED**: Returns do not justify the investment risk."
        
        return report
    
    def _store_scenario(self, scenario: ROIScenario):
        """Store ROI scenario in database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO roi_scenarios
                (scenario_id, name, description, analysis_period_months, discount_rate, risk_factor)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                scenario.scenario_id,
                scenario.name,
                scenario.description,
                scenario.analysis_period_months,
                scenario.discount_rate,
                scenario.risk_factor
            ))
    
    def _store_cost_item(self, scenario_id: str, cost: CostItem):
        """Store cost item in database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cost_items
                (cost_id, scenario_id, name, cost_type, amount, frequency, start_date, end_date, allocated_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cost.cost_id,
                scenario_id,
                cost.name,
                cost.cost_type.value,
                cost.amount,
                cost.frequency,
                cost.start_date.isoformat(),
                cost.end_date.isoformat() if cost.end_date else None,
                cost.allocated_percentage
            ))
    
    def _store_benefit_item(self, scenario_id: str, benefit: BenefitItem):
        """Store benefit item in database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO benefit_items
                (benefit_id, scenario_id, name, benefit_type, amount, frequency, start_date, end_date, confidence, realization_curve)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                benefit.benefit_id,
                scenario_id,
                benefit.name,
                benefit.benefit_type.value,
                benefit.amount,
                benefit.frequency,
                benefit.start_date.isoformat(),
                benefit.end_date.isoformat() if benefit.end_date else None,
                benefit.confidence,
                benefit.realization_curve
            ))
    
    def _store_roi_result(self, result: ROIResult):
        """Store ROI result in database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            result_id = f"result_{int(result.calculation_date.timestamp())}"
            
            conn.execute("""
                INSERT OR REPLACE INTO roi_results
                (result_id, scenario_id, calculation_date, roi_percentage, npv, payback_months,
                 total_costs, total_benefits, confidence_low, confidence_high, results_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result_id,
                result.scenario_id,
                result.calculation_date.isoformat(),
                result.roi_percentage,
                result.net_present_value,
                result.payback_period_months,
                result.total_costs,
                result.total_benefits,
                result.confidence_interval[0],
                result.confidence_interval[1],
                json.dumps(asdict(result), default=str)
            ))
    
    def _load_scenario(self, scenario_id: str) -> Optional[ROIScenario]:
        """Load scenario from database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM roi_scenarios WHERE scenario_id = ?",
                (scenario_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return ROIScenario(
                    scenario_id=row['scenario_id'],
                    name=row['name'],
                    description=row['description'] or "",
                    costs=[],
                    benefits=[],
                    analysis_period_months=row['analysis_period_months'],
                    discount_rate=row['discount_rate'],
                    risk_factor=row['risk_factor']
                )
        
        return None
    
    def _load_cost_items(self, scenario_id: str) -> List[CostItem]:
        """Load cost items from database"""
        costs = []
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM cost_items WHERE scenario_id = ?",
                (scenario_id,)
            )
            
            for row in cursor:
                cost = CostItem(
                    cost_id=row['cost_id'],
                    name=row['name'],
                    cost_type=CostType(row['cost_type']),
                    amount=row['amount'],
                    frequency=row['frequency'],
                    start_date=datetime.fromisoformat(row['start_date']),
                    end_date=datetime.fromisoformat(row['end_date']) if row['end_date'] else None,
                    allocated_percentage=row['allocated_percentage']
                )
                costs.append(cost)
        
        return costs
    
    def _load_benefit_items(self, scenario_id: str) -> List[BenefitItem]:
        """Load benefit items from database"""
        benefits = []
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM benefit_items WHERE scenario_id = ?",
                (scenario_id,)
            )
            
            for row in cursor:
                benefit = BenefitItem(
                    benefit_id=row['benefit_id'],
                    name=row['name'],
                    benefit_type=BenefitType(row['benefit_type']),
                    amount=row['amount'],
                    frequency=row['frequency'],
                    start_date=datetime.fromisoformat(row['start_date']),
                    end_date=datetime.fromisoformat(row['end_date']) if row['end_date'] else None,
                    confidence=row['confidence'],
                    realization_curve=row['realization_curve']
                )
                benefits.append(benefit)
        
        return benefits