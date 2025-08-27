"""
Thompson Sampling algorithm implementation
"""

import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ThompsonSampling:
    """
    Thompson Sampling algorithm for Multi-Armed Bandit optimization
    Uses Beta distribution to model click-through rates for each variant
    """
    
    def __init__(
        self,
        alpha_prior: float = 1.0,
        beta_prior: float = 1.0,
        min_explore_rate: float = 0.05,
        control_floor: float = 0.1,
        max_daily_shift: float = 0.2
    ):
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
        self.min_explore_rate = min_explore_rate
        self.control_floor = control_floor
        self.max_daily_shift = max_daily_shift
        
        # Set random seed for reproducibility
        np.random.seed(42)
    
    def calculate_allocation(
        self, 
        variant_data: List[Dict], 
        previous_allocation: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        Calculate optimal traffic allocation using Thompson Sampling
        
        Args:
            variant_data: List of dicts with keys: name, impressions, clicks
            previous_allocation: Previous day's allocation for smoothing
            
        Returns:
            Dictionary mapping variant names to allocation percentages
        """
        
        if not variant_data:
            raise ValueError("No variant data provided")
        
        # Check if we have enough data for optimization
        total_impressions = sum(v.get("impressions", 0) for v in variant_data)
        if total_impressions < 1000:  # Warmup period
            logger.info("Insufficient data for optimization, using uniform allocation")
            return self._uniform_allocation(variant_data)
        
        # Calculate posterior parameters for each variant
        posteriors = {}
        for variant in variant_data:
            name = variant["name"]
            impressions = variant.get("impressions", 0)
            clicks = variant.get("clicks", 0)
            
            # Beta distribution parameters
            alpha = self.alpha_prior + clicks
            beta_param = self.beta_prior + (impressions - clicks)
            
            posteriors[name] = {"alpha": alpha, "beta": beta_param}
        
        # Sample from posterior distributions
        samples = {}
        for name, params in posteriors.items():
            theta = np.random.beta(params["alpha"], params["beta"])
            samples[name] = theta
        
        logger.info(f"Thompson Sampling - Posterior samples: {samples}")
        
        # Calculate raw allocation based on samples
        total_sample = sum(samples.values())
        raw_allocation = {name: theta / total_sample for name, theta in samples.items()}
        
        # Apply safety constraints
        safe_allocation = self._apply_constraints(raw_allocation, previous_allocation)
        
        # Normalize to sum to 1.0
        total = sum(safe_allocation.values())
        normalized_allocation = {
            name: round(alloc / total, 4) 
            for name, alloc in safe_allocation.items()
        }
        
        logger.info(f"Final allocation: {normalized_allocation}")
        return normalized_allocation
    
    def _uniform_allocation(self, variant_data: List[Dict]) -> Dict[str, float]:
        """Return uniform allocation when insufficient data"""
        n_variants = len(variant_data)
        allocation = 1.0 / n_variants
        return {v["name"]: round(allocation, 4) for v in variant_data}
    
    def _apply_constraints(
        self, 
        allocation: Dict[str, float],
        previous_allocation: Dict[str, float] = None
    ) -> Dict[str, float]:
        """Apply safety constraints to allocation"""
        constrained = allocation.copy()
        
        # 1. Apply minimum exploration rate
        n_variants = len(constrained)
        
        for name in constrained:
            uniform_component = 1.0 / n_variants
            constrained[name] = (
                (1 - self.min_explore_rate) * constrained[name] + 
                self.min_explore_rate * uniform_component
            )
        
        # 2. Apply control floor
        if "control" in constrained:
            if constrained["control"] < self.control_floor:
                deficit = self.control_floor - constrained["control"]
                constrained["control"] = self.control_floor
                
                other_variants = [k for k in constrained if k != "control"]
                if other_variants:
                    for variant in other_variants:
                        constrained[variant] -= deficit / len(other_variants)
                        constrained[variant] = max(0, constrained[variant])
        
        # 3. Apply maximum daily shift constraint
        if previous_allocation:
            for name in constrained:
                previous = previous_allocation.get(name, constrained[name])
                shift = constrained[name] - previous
                
                if abs(shift) > self.max_daily_shift:
                    if shift > 0:
                        constrained[name] = previous + self.max_daily_shift
                    else:
                        constrained[name] = previous - self.max_daily_shift
        
        return constrained