from datetime import datetime

import langchain
from langchain.agents import initialize_agent, AgentType
from langchain.chains.llm import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory

from langchain_core.globals import set_verbose
from langchain_core.tools import tool, BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from core.conf import OPENAI_API_KEY


#просто старое приложение, можешь глянуть, нам не оч актуально пока

template = """Ты являетесь помощником по ответу на 
вопросы. Тебе предоставлена часть контекста, содержащая информацию по вопросу пользователя. 
Отвечай только в рамках предоставленного контекста.
Если предоставленный контекст не содержит ответ на вопрос пользователя, отвечай отрицательно. 
Не придумывай дополнительную информацию. 
Отвечайте лаконично, общайся лично. 
Тебе предоставлена часть истории сообщений с пользователем, твоя задача - ответить на последнее сообщение пользователя.
Учитывай историю сообщений и контекст.
Отвечай только на языке пользователя.


Контекст: 
-----
{context}
-----


Часть истории сообщений: 
-----
{history}
AI: (твой ответ здесь)
-----

"""

lang_template = """Определи язык сообщения пользователя.
Пример ответа: русский

Сообщение: 
-----
{mess}
-----

"""

question_templater = """Я являюсь AI ассистентом, который анализирует последние сообщения и формирует расширенные, более детализированные запросы на их основе. 
Ниже приведен пример последних сообщений, на основе которых необходимо сформулировать новый запрос, проведи суммаризацию. 
Тебе надо расширить только последнее сообщение.
Будь краток. Не добавляй дополнительную информацию.
Не додумывай!
Будь лаконичен.
Ты не должен отвечать на вопрос пользователя, ты только переформулируешь его.
Ты не можешь переспрашивать или простить дополнительную информацию

Предыдущие сообщения:
-----
{history}
-----

Сформулируй расширенный и более детальный запрос на основе предыдущих сообщений:

"""




class QuestionAnswering:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.question_llm = ChatOpenAI(model_name="gpt-4o-2024-05-13", temperature=0,
                                       openai_api_key=self.api_key, verbose=True)
        self.answer_llm = ChatOpenAI(model_name="gpt-4-turbo-2024-04-09", temperature=0,
                                     openai_api_key=self.api_key, verbose=True)
        self.contex = ""
        self.memory = ConversationBufferWindowMemory(k=10, human_prefix="Пользователь", ai_prefix="AI")

        self.prompt = PromptTemplate(
            input_variables=[
                "contex"],  # add хистори если суммаризация
            template=template,
            partial_variables={
                "history": self.get_history,  # elfkb это если суммаризация
            }
        )

    def clear_memory(self):
        self.memory.clear()

    def get_contex(self, message):
        return self.contex

    def get_history(self):
        return self.memory.buffer_as_str

    def c_h(self, message):
        print("ok")

    def get_answer(self, question):
        self.memory.chat_memory.add_user_message(question)  # delete если сумм



        set_verbose(True)
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.answer_llm,
            chain_type='stuff',
            verbose=True,
            chain_type_kwargs={'prompt': self.prompt},  # 'memory': self.memory
        )

        result = qa_chain.invoke()

        print(result)
        green = template.format(history=self.get_history())
        self.memory.chat_memory.add_ai_message(result["result"])  # delete если сумм

        return result["result"], green
