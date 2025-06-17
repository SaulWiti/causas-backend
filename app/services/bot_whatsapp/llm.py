from langchain_openai import AzureChatOpenAI

gpt_4o = AzureChatOpenAI(temperature=0.2, model="gpt-4o", seed=250)
gpt_4o_mini = AzureChatOpenAI(temperature=0.2, model="gpt-4o-mini", seed=250)