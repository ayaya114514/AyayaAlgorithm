"""Validated, versioned problem import format."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Example(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input: str = Field(max_length=262144)
    output: str = Field(max_length=262144)


class Problem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$")
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=32)
    tags: list[str] = Field(default_factory=list, max_length=12)
    difficulty: Literal["入门", "基础", "进阶"] = "基础"
    score: int = Field(default=20, ge=1, le=100)
    statement: str = Field(min_length=1, max_length=30000)
    input_format: str = Field(min_length=1, max_length=5000)
    output_format: str = Field(min_length=1, max_length=5000)
    constraints: str = Field(default="", max_length=5000)
    samples: list[Example] = Field(min_length=1, max_length=10)
    tests: list[Example] = Field(min_length=1, max_length=100)
    time_limit_ms: int = Field(default=2000, ge=200, le=10000)
    memory_limit_mb: int = Field(default=256, ge=32, le=1024)
    comparator: Literal["tokens", "exact"] = "tokens"
    source: str = Field(default="个人导入", max_length=300)
    source_url: str = Field(default="", max_length=1000)
    provenance: str = Field(default="个人提供的题面与测试数据", max_length=2000)
    editorial: str = Field(default="", max_length=10000)

    @model_validator(mode="after")
    def validate_size(self):
        if any(len(tag) > 40 for tag in self.tags):
            raise ValueError("每个标签最多 40 字符")
        if sum(len(t.input.encode()) + len(t.output.encode()) for t in self.tests) > 1500000:
            raise ValueError("测试数据总计不能超过 1.5 MB")
        if self.source_url and not self.source_url.startswith(("https://", "http://")):
            raise ValueError("来源链接必须是 http 或 https URL")
        return self

    def public(self):
        return self.model_dump(exclude={"tests"}) | {"test_count": len(self.tests)}


class SubmissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    problem_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$")
    language: Literal["c", "cpp", "python"]
    code: str = Field(min_length=1, max_length=100000)
    mode: Literal["judge", "sample", "custom"] = "judge"
    stdin: str = Field(default="", max_length=262144)
