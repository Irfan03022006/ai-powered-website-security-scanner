"""Scan model: one row per security scan run."""

from datetime import datetime, timezone

from models.database import db


class Scan(db.Model):
    __tablename__ = "scans"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    security_score = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), default="pending")  # pending|running|completed|failed
    error_message = db.Column(db.String(1024), nullable=True)

    findings = db.relationship(
        "Finding", backref="scan", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, include_findings: bool = False):
        data = {
            "id": self.id,
            "url": self.url,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "security_score": self.security_score,
            "status": self.status,
            "error_message": self.error_message,
        }
        if include_findings:
            data["findings"] = [f.to_dict() for f in self.findings]
        return data
