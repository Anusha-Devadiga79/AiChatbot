import json
import os
from datetime import datetime
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

class ReportAnalyzer:
    """Analyze medical reports with in-context learning from previous reports."""
    
    def __init__(self):
        self.client = client
        self.knowledge_base = {}
    
    def analyze_report(self, report_data, previous_reports=None):
        """
        Analyze current report with context from previous reports.
        
        Args:
            report_data: Current report data {patient_name, age, gender, report_text}
            previous_reports: List of previous report analyses for comparison
        
        Returns:
            Analysis result with health summary
        """
        if not self.client:
            return self._fallback_analysis(report_data, previous_reports)
        
        try:
            # Build enhanced prompt with previous reports context
            enhanced_prompt = self._build_enhanced_prompt(report_data, previous_reports)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medical report analyzer. Analyze the provided medical report and:
1. Identify key health indicators and their values
2. Compare with previous reports if available
3. Highlight any concerning trends
4. Provide health summary and recommendations
5. Note any improvements or deterioration

Format response with clear sections:
- KEY FINDINGS
- COMPARISON WITH PREVIOUS REPORTS (if available)
- HEALTH TRENDS
- RECOMMENDATIONS
- OVERALL HEALTH SUMMARY"""
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis,
                "model": "gpt-4-turbo",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Report analysis error: {str(e)}")
            return self._fallback_analysis(report_data, previous_reports)
    
    def _build_enhanced_prompt(self, report_data, previous_reports):
        """Build prompt with context from previous reports."""
        prompt = f"""Analyze the following medical report:

Patient: {report_data.get('patient_name', 'Unknown')}
Age: {report_data.get('age', 'Unknown')}
Gender: {report_data.get('gender', 'Unknown')}

Current Report:
{report_data.get('report_text', '')}
"""
        
        # Add previous reports context if available
        if previous_reports and len(previous_reports) > 0:
            prompt += "\n\nPrevious Reports for Comparison:\n"
            for i, prev_report in enumerate(previous_reports[-3:], 1):  # Last 3 reports
                prompt += f"\nReport {i} (Date: {prev_report.get('date', 'Unknown')}):\n"
                prompt += f"{prev_report.get('analysis', '')}\n"
        
        return prompt
    
    def _fallback_analysis(self, report_data, previous_reports):
        """Fallback analysis when API is unavailable."""
        analysis = f"""Medical Report Analysis

Patient: {report_data.get('patient_name', 'Unknown')}
Age: {report_data.get('age', 'Unknown')}
Gender: {report_data.get('gender', 'Unknown')}

KEY FINDINGS:
- Report received and processed
- Please consult with a healthcare professional for detailed analysis

OVERALL HEALTH SUMMARY:
This report has been received. For comprehensive analysis, please consult with a qualified medical professional.

Note: This is for awareness purposes only. Always consult a qualified healthcare professional."""
        
        return {
            "success": True,
            "analysis": analysis,
            "model": "fallback",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def translate_analysis(self, analysis_text, target_language):
        """Translate analysis to target language."""
        if not self.client:
            return analysis_text
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Translate the following medical report analysis to {target_language}. Keep the structure and formatting."
                    },
                    {
                        "role": "user",
                        "content": analysis_text
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return analysis_text
