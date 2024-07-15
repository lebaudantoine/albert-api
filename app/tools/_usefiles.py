import sys
from typing import List, Optional

from fastapi import HTTPException

sys.path.append("..")
from utils.data import file_to_chunk
from utils.security import secure_data


class UseFiles:
    """
    Fill your prompt with file contents. Your prompt must contain "{files}" placeholder.

    Args:
        collection (str): Collection name.
        file_ids (List[str]): List of file ids in the selected collection.
    """

    DEFAULT_PROMPT_TEMPLATE = "Réponds à la question suivante en te basant sur les documents ci-dessous : %(prompt)s\n\nDocuments :\n\n%(docs)s"

    def __init__(self, clients: dict):
        self.clients = clients

    @secure_data
    async def get_prompt(
        self,
        collection: str,
        file_ids: Optional[List[str]] = None,
        **request,
    ) -> str:
        if "user" not in request:
            raise HTTPException(
                status_code=400, detail="User parameter must be provide with UseFiles tool."
            )
        prompt = request["messages"][-1]["content"]
        if "{files}" not in prompt:
            raise HTTPException(
                status_code=400, detail='User message must contain "{files}" with UseFiles tool.'
            )
        data = file_to_chunk(
            client=self.clients["vectors"], collection=collection, file_ids=file_ids
        )
        if not data:
            raise HTTPException(status_code=404, detail="Files not found.")
        files = "\n\n".join([vector["chunk"] for vector in data])
        prompt = prompt.replace("{files}", files)

        return prompt
