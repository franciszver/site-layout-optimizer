"""
AI optimization engine using OpenAI GPT-4o via OpenRouter
"""
import json
from typing import Dict, Any, List, Optional
import httpx
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings


class AIOptimizer:
    """AI-powered optimization and constraint analysis"""
    
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openai_model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def analyze_constraints(
        self,
        property_data: Dict[str, Any],
        asset_requirements: List[Dict[str, Any]],
        existing_constraints: Dict[str, Any],
        regulatory_constraints: Optional[Dict[str, Any]] = None,
        terrain_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze constraints and provide recommendations using AI
        
        Args:
            property_data: Property boundaries and metadata
            asset_requirements: Assets to place
            existing_constraints: Exclusion zones, buffers, etc.
            regulatory_constraints: FEMA, EPA, zoning data
            terrain_analysis: Terrain metrics
        
        Returns:
            AI analysis with recommendations
        """
        prompt = self._build_analysis_prompt(
            property_data,
            asset_requirements,
            existing_constraints,
            regulatory_constraints,
            terrain_analysis
        )
        
        response = self._call_openai(prompt)
        
        return {
            'recommendations': response.get('recommendations', []),
            'constraint_violations': response.get('violations', []),
            'optimization_suggestions': response.get('suggestions', []),
            'risk_assessment': response.get('risks', []),
            'reasoning': response.get('reasoning', '')
        }
    
    def optimize_layout(
        self,
        current_layout: Dict[str, Any],
        optimization_goals: List[str],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate optimized layout recommendations
        
        Args:
            current_layout: Current asset placements
            optimization_goals: List of goals (e.g., ['minimize_cut_fill', 'maximize_utilization'])
            constraints: All constraints
        
        Returns:
            Optimization recommendations
        """
        prompt = self._build_optimization_prompt(
            current_layout,
            optimization_goals,
            constraints
        )
        
        response = self._call_openai(prompt)
        
        return {
            'optimized_layout': response.get('layout', {}),
            'improvements': response.get('improvements', []),
            'metrics': response.get('metrics', {}),
            'trade_offs': response.get('trade_offs', [])
        }
    
    def _build_analysis_prompt(
        self,
        property_data: Dict[str, Any],
        asset_requirements: List[Dict[str, Any]],
        existing_constraints: Dict[str, Any],
        regulatory_constraints: Optional[Dict[str, Any]],
        terrain_analysis: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for constraint analysis"""
        prompt = f"""Analyze the following site layout for real estate due diligence:

Property: {json.dumps(property_data, indent=2)}
Assets to place: {json.dumps(asset_requirements, indent=2)}
Existing Constraints: {json.dumps(existing_constraints, indent=2)}
"""
        
        if regulatory_constraints:
            prompt += f"Regulatory Constraints: {json.dumps(regulatory_constraints, indent=2)}\n"
        
        if terrain_analysis:
            prompt += f"Terrain Analysis: {json.dumps(terrain_analysis, indent=2)}\n"
        
        prompt += """
Provide comprehensive recommendations:
1. Optimal asset placement locations with reasoning
2. Constraint violations to avoid (regulatory, environmental, terrain)
3. Road network optimization (minimize length, avoid steep grades)
4. Cut/fill optimization strategies (minimize earthwork)
5. Regulatory compliance check (zoning, setbacks, environmental)
6. Alternative layout options with trade-offs
7. Risk assessment for proposed layout

Format your response as JSON with the following structure:
{
  "recommendations": [{"location": [x, y], "reasoning": "..."}],
  "violations": [{"type": "...", "severity": "...", "description": "..."}],
  "suggestions": [{"type": "...", "description": "..."}],
  "risks": [{"type": "...", "severity": "...", "description": "..."}],
  "reasoning": "Overall analysis and reasoning"
}
"""
        return prompt
    
    def _build_optimization_prompt(
        self,
        current_layout: Dict[str, Any],
        optimization_goals: List[str],
        constraints: Dict[str, Any]
    ) -> str:
        """Build prompt for layout optimization"""
        prompt = f"""Optimize the following site layout:

Current Layout: {json.dumps(current_layout, indent=2)}
Optimization Goals: {', '.join(optimization_goals)}
Constraints: {json.dumps(constraints, indent=2)}

Provide optimized layout recommendations considering:
- Site utilization efficiency
- Cut/fill volume minimization
- Road length minimization
- Constraint compliance
- Cost-benefit analysis

Format your response as JSON:
{{
  "layout": {{"assets": [...], "roads": [...]}},
  "improvements": [{{"type": "...", "description": "...", "impact": "..."}}],
  "metrics": {{"utilization": 0.0, "cut_fill_reduction": 0.0, "road_length_reduction": 0.0}},
  "trade_offs": [{{"option": "...", "pros": [...], "cons": [...]}}]
}}
"""
        return prompt
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API via OpenRouter with caching"""
        if not self.api_key:
            # Fallback to rule-based if no API key
            return self._fallback_analysis()
        
        # Check cache first (cache by prompt hash to avoid duplicate calls)
        from utils.cache import get_cached, set_cached, generate_cache_key
        cache_key = generate_cache_key("ai_optimizer", prompt)
        cached_result = get_cached(cache_key)
        if cached_result is not None:
            return cached_result
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a geospatial site layout optimization expert. Provide detailed, technical recommendations for real estate due diligence."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    parsed_result = json.loads(content)
                except json.JSONDecodeError:
                    # If response is not JSON, return as reasoning
                    parsed_result = {
                        'reasoning': content,
                        'recommendations': [],
                        'violations': [],
                        'suggestions': []
                    }
                
                # Cache the result (1 hour TTL)
                set_cached(cache_key, parsed_result, ttl=3600)
                return parsed_result
        except Exception as e:
            # Fallback on error
            return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback rule-based analysis if AI unavailable"""
        return {
            'recommendations': [
                {
                    'location': None,
                    'reasoning': 'AI analysis unavailable. Using rule-based optimization.'
                }
            ],
            'violations': [],
            'suggestions': [
                {
                    'type': 'general',
                    'description': 'Place assets on flatter terrain (<5% slope)'
                },
                {
                    'type': 'general',
                    'description': 'Maintain minimum spacing between assets'
                }
            ],
            'risks': [],
            'reasoning': 'Rule-based analysis: Prioritize flat terrain, maintain buffers, minimize road length.'
        }

