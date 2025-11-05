"""DTO для JSON-ответов от LLM."""
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class JSONResponse:
    """DTO для структурированного JSON-ответа от LLM."""
    
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return {
            "status": self.status,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }
    
    @classmethod
    def success(cls, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> "JSONResponse":
        """Создать успешный ответ."""
        return cls(status="success", data=data, metadata=metadata)
    
    @classmethod
    def error(cls, error_message: str, metadata: Optional[Dict[str, Any]] = None) -> "JSONResponse":
        """Создать ответ с ошибкой."""
        return cls(status="error", error=error_message, metadata=metadata)