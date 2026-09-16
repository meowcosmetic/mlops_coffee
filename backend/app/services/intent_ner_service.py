"""Intent & Named Entity Recognition (NER) Service for DrinkBot.

Extracts customer delivery details (Name, Phone number, Shipping Address)
and structured order items directly from unstructured Vietnamese chat messages.
Supports both regex/heuristic fast-path and LLM extraction fallback.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Vietnamese phone number pattern: 10 digits starting with 03, 05, 07, 08, 09 or +84
PHONE_PATTERN = re.compile(r"(?:\+84|0)(?:3|5|7|8|9)\d{8}\b")

# Vietnamese customer name cues: anh/chị/bạn/em [Name]
NAME_PATTERNS = [
    re.compile(r"(?:giao cho|cho|đặt cho|gửi cho|tên là|tôi là)\s+((?:anh|chị|bạn|em|cô|chú)?\s*[A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)", re.IGNORECASE),
    re.compile(r"(?:khách hàng|người nhận|tên)\s*[:\-]?\s*([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)", re.IGNORECASE),
]

# Vietnamese address cues: đến/tại/ở [Số nhà Đường/Phố/Quận...]
ADDRESS_PATTERNS = [
    re.compile(r"(?:đến|giao đến|tại|ở|địa chỉ)\s+([0-9]+[A-Za-z]?\s+[\w\s\u00C0-\u1EF9]+(?:đường|phố|ngõ|ngách|quận|phường|huyện|thành phố|tp|tòa|chung cư|số)?[\w\s\u00C0-\u1EF9,]*)", re.IGNORECASE),
    re.compile(r"(?:địa chỉ|đc)\s*[:\-]?\s*([0-9\w\s\u00C0-\u1EF9,/.\-]+)", re.IGNORECASE),
]

# Quantity item patterns
QUANTITY_ITEM_PATTERNS = [
    re.compile(r"(\d+)\s*(?:ly|cốc|phần|chai|suất)?\s+([A-Za-zÀ-Ỹà-ỹ\s]+?)(?=(?:và|hoặc|,|\.|\n|đến|số|sđt|$))", re.IGNORECASE),
]


@dataclass
class ExtractedEntities:
    customer_name: str | None = None
    phone_number: str | None = None
    shipping_address: str | None = None
    items: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    raw_query: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_name": self.customer_name,
            "phone_number": self.phone_number,
            "shipping_address": self.shipping_address,
            "items": self.items,
            "confidence": self.confidence,
            "has_delivery_info": bool(self.shipping_address or self.phone_number),
        }


class IntentNERService:
    """Lightweight & fast entity extractor for Vietnamese F&B delivery orders."""

    def extract(self, text: str) -> ExtractedEntities:
        """Extract delivery metadata and items from user chat."""
        cleaned = text.strip()
        entities = ExtractedEntities(raw_query=cleaned)

        # 1. Phone number
        phone_match = PHONE_PATTERN.search(cleaned)
        if phone_match:
            entities.phone_number = phone_match.group(0)

        # 2. Customer Name
        for pat in NAME_PATTERNS:
            name_match = pat.search(cleaned)
            if name_match:
                extracted = name_match.group(1).strip()
                extracted = re.split(r"\s+(?:số|sđt|ở|tại|đến|\d+)\b", extracted, flags=re.IGNORECASE)[0].strip()
                # Exclude common false positives
                if extracted.lower() not in ("ly", "cốc", "quán", "em", "mình", "tôi", "cho"):
                    entities.customer_name = extracted.title()
                    break

        # 3. Address
        for pat in ADDRESS_PATTERNS:
            addr_match = pat.search(cleaned)
            if addr_match:
                addr_text = addr_match.group(1).strip()
                # Clean up trailing conjunctions or phone markers
                addr_text = re.split(r"(?:sđt|số điện thoại|alo|gọi|nhé|nha|sdt|\b0\d{9})", addr_text, flags=re.IGNORECASE)[0].strip()
                if len(addr_text) >= 5:
                    entities.shipping_address = addr_text
                    break

        # 4. Items & Quantities
        items: list[dict[str, Any]] = []
        for pat in QUANTITY_ITEM_PATTERNS:
            for m in pat.finditer(cleaned):
                qty = int(m.group(1))
                raw_name = m.group(2).strip()
                # Clean unwanted tokens
                raw_name = re.sub(r"^(ly|cốc|phần|chai)\s*", "", raw_name, flags=re.IGNORECASE).strip()
                if raw_name and len(raw_name) > 2 and raw_name.lower() not in ("số", "đến", "cho"):
                    items.append({"item": raw_name.title(), "quantity": qty})

        entities.items = items

        # Confidence calculation
        found_fields = sum(bool(x) for x in [entities.customer_name, entities.phone_number, entities.shipping_address])
        entities.confidence = round(found_fields / 3.0, 2) if found_fields > 0 else 0.0

        return entities


ner_service = IntentNERService()
