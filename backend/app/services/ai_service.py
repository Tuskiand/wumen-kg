from __future__ import annotations

import json
from datetime import datetime
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.ai_config import AiConfig


class AiService:
    def __init__(self, settings: Settings, db_session: Session) -> None:
        self.settings = settings
        self.db_session = db_session

    def _get_config(self) -> AiConfig:
        config = self.db_session.query(AiConfig).first()
        if config is None:
            config = AiConfig(api_key="", base_url="https://api.deepseek.com/v1", model="deepseek-chat")
            self.db_session.add(config)
            self.db_session.commit()
        return config

    def get_config_response(self) -> dict:
        config = self._get_config()
        return {
            "base_url": config.base_url,
            "model": config.model,
            "has_key": bool(config.api_key),
        }

    def update_config(self, api_key: str, base_url: str, model: str) -> None:
        config = self._get_config()
        config.api_key = api_key
        config.base_url = base_url
        config.model = model
        self.db_session.commit()

    def analyze_physician_compare(
        self,
        disease: str,
        doctors: list[str],
        node_summary: str,
        path_summary: str,
        subgraph_summary: str,
    ) -> tuple[str, str]:
        config = self._get_config()
        if not config.api_key:
            return "未配置 LLM API Key，请在管理端设置大模型参数。", config.model

        system_prompt = """你是一位中医知识图谱分析专家。根据医家比较的量化指标，为研究人员提供易理解的综合分析。

分析要求：
1. 一句话概括整体结论
2. 从节点相似度、辨证路径、核心子图三个层面简要解读
3. 指出各医家辨证特点差异

语言专业易懂，关注临床意义，控制篇幅。"""

        user_prompt = f"""病名「{disease}」，医家：{', '.join(doctors)}。

## 节点比较
{node_summary}

## 辨证路径
{path_summary}

## 核心子图
{subgraph_summary}

请给出综合分析。"""

        return self._call_llm(system_prompt, user_prompt, config, timeout=120)

    def _call_llm(self, system_prompt: str, user_prompt: str, config: AiConfig, timeout: int = 120) -> tuple[str, str]:
        payload = json.dumps({
            "model": config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.5,
            "max_tokens": 1500,
        }).encode()

        url = f"{config.base_url.rstrip('/')}/chat/completions"
        req = Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}",
        })

        try:
            with urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
                content = data["choices"][0]["message"]["content"]
                return content, config.model
        except Exception as exc:
            return f"AI 分析调用失败：{exc}", config.model

    def test_connection(self, api_key: str, base_url: str, model: str) -> tuple[bool, str]:
        config = AiConfig(
            api_key=api_key, base_url=base_url, model=model,
            id=0, updated_at=datetime.now(),
        )
        result, _ = self._call_llm("Respond OK", "OK", config, timeout=15)
        if result.startswith("AI 分析调用失败"):
            return False, result
        return True, f"连接成功，模型响应正常"