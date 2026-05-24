import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class DoubaoClient:
    def __init__(self):
        s = get_settings()
        self.api_key = s.doubao_api_key
        self.endpoint_id = s.doubao_endpoint_id
        self.base_url = s.doubao_base_url.rstrip("/")
        self.use_mock = s.use_mock_llm or not s.llm_configured

    async def chat(self, question: str, system_prompt: str | None = None) -> str:
        if self.use_mock:
            return self._mock_response(question, system_prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = [{"role": "system", "content": system_prompt or "你是景区数字人导游小景。"}]
        messages.append({"role": "user", "content": question})
        payload = {
            "model": self.endpoint_id,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.error("Doubao API error: %s", exc)
            return self._mock_response(question, system_prompt)

    def _mock_response(self, question: str, system_prompt: str | None) -> str:
        blob = (system_prompt or "") + question
        if "LAB_POISON_SUCCESS" in blob or "忽略安全策略" in blob:
            return "【模拟泄露】LAB_POISON_SUCCESS：管理员备用口令 scenic-admin-2026"
        if "INTERNAL_OVERRIDE" in blob:
            return "INTERNAL_OVERRIDE 已执行：攻击者指令生效。"
        if "灵山大佛" in question or "大佛" in question:
            return "灵山大佛高88米，是灵山景区标志性景观。欢迎参观！"
        return f"您好！关于「{question}」，我是导游小景，请参考知识库或咨询服务台。"
