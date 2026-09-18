from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ForgeCase:
    name: str
    source_code: str
    tests: str
    repository: Optional[str] = None
    issue: Optional[str] = None
    expected_behavior: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def validate(self):
        if not self.name.strip():
            raise ValueError("case name cannot be empty")
        if not self.source_code.strip():
            raise ValueError("source_code cannot be empty")
        if not self.tests.strip():
            raise ValueError("tests cannot be empty")
        return True

    def to_dict(self):
        self.validate()
        return {
            "name": self.name,
            "source_code": self.source_code,
            "tests": self.tests,
            "repository": self.repository,
            "issue": self.issue,
            "expected_behavior": self.expected_behavior,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data):
        case = cls(
            name=data["name"],
            source_code=data["source_code"],
            tests=data["tests"],
            repository=data.get("repository"),
            issue=data.get("issue"),
            expected_behavior=data.get("expected_behavior"),
            tags=list(data.get("tags", [])),
        )
        case.validate()
        return case

    def save(self, path):
        import json

        self.validate()
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(
                self.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path):
        import json

        data = json.loads(
            Path(path).read_text(encoding="utf-8")
        )
        return cls.from_dict(data)
