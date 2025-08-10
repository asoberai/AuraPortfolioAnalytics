#!/usr/bin/env python3
"""
AuraQuant API Response Utility
Standardized response format for API operations
"""

from typing import Any, Optional, Dict
from dataclasses import dataclass

@dataclass
class APIResponse:
    """
    Standardized API response format
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            'success': self.success
        }
        
        if self.data is not None:
            result['data'] = self.data
            
        if self.error is not None:
            result['error'] = self.error
            
        if self.metadata is not None:
            result['metadata'] = self.metadata
            
        return result

def success_response(data: Any = None, metadata: Dict[str, Any] = None) -> APIResponse:
    """Create a success response"""
    return APIResponse(success=True, data=data, metadata=metadata)

def error_response(error: str, metadata: Dict[str, Any] = None) -> APIResponse:
    """Create an error response"""
    return APIResponse(success=False, error=error, metadata=metadata) 