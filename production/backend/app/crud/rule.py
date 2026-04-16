from sqlalchemy.orm import Session
from ..models.rule import Rule
import json

def create_rule(db: Session, rule_data: dict):
    rule_data["escalation_json"] = json.dumps(rule_data["escalation"])
    del rule_data["escalation"]
    db_rule = Rule(**rule_data)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule
