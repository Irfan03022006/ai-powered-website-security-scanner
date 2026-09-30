"""Finding model: one row per individual scan finding."""

from models.database import db


class Finding(db.Model):
    __tablename__ = "findings"

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey("scans.id"), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # High/Medium/Low/Informational
    description = db.Column(db.Text, nullable=True)
    evidence = db.Column(db.Text, nullable=True)
    impact = db.Column(db.Text, nullable=True)
    recommendation = db.Column(db.Text, nullable=True)
    scanner_module = db.Column(db.String(100), nullable=True)

    # AI explanation fields (stored so reports don't need to re-call the AI)
    ai_what_it_means = db.Column(db.Text, nullable=True)
    ai_why_it_matters = db.Column(db.Text, nullable=True)
    ai_possible_impact = db.Column(db.Text, nullable=True)
    ai_recommended_action = db.Column(db.Text, nullable=True)
    ai_priority = db.Column(db.String(20), nullable=True)
    ai_source = db.Column(db.String(20), nullable=True)  # 'ai' or 'fallback'

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "evidence": self.evidence,
            "impact": self.impact,
            "recommendation": self.recommendation,
            "scanner_module": self.scanner_module,
            "ai_explanation": {
                "what_it_means": self.ai_what_it_means,
                "why_it_matters": self.ai_why_it_matters,
                "possible_impact": self.ai_possible_impact,
                "recommended_action": self.ai_recommended_action,
                "priority": self.ai_priority,
                "source": self.ai_source,
            },
        }
