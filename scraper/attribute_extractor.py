from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import pandas as pd
import json
from settings import settings


# Pydantic model for structured output
class Product(BaseModel):
    """A class to represent a product with its attributes."""

    brand: str
    model: str
    flavor: list[str] | str | None
    puff_count: str
    nicotine_strength: str
    battery_capacity: str
    coil_type: str
    category: str


class AtrributeExtractor:
    """
    A class to extract product attributes using a language model.
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=0.1,
            api_key=settings.GROQ_API_KEY,
        )

    async def extract_attributes(self, text: str) -> Product:
        prompt = PromptTemplate.from_template("""
You are given the description of a vape product as {context}.
Extract and return the following attributes in JSON format:
brand: The manufacturer or brand name of the vape.
model/type: The specific model name, type, or series identifier.
flavor: A list of all flavors mentioned in the description. Always return this as a list, even if only one flavor is present.
puff_count: The total number of puffs the product offers.
nicotine_strength: The nicotine content or strength.
battery_capacity: The battery capacity.
coil_type: The type of coil used.
category: The product category.
If any attribute is not available in the context, return "NAN" for that attribute.
""")
        chain = prompt | self.llm.with_structured_output(Product)
        response = await chain.ainvoke({"context": text})
        return response

    async def extract(
        self,
        csv_file: str = "vapewholesalesusa_data.csv",
        output_json: str = "structured_output.jsonl",
    ):
        df = pd.read_csv(csv_file)

        if "more_information" in df.columns and "description" in df.columns:
            joined_list = (
                df["more_information"].fillna("") + " " + df["description"].fillna("")
            ).tolist()
        elif "description" in df.columns:
            joined_list = df["description"].fillna("").tolist()
        else:
            joined_list = []

        with open(output_json, "w") as f:
            for i, text in enumerate(joined_list):
                try:
                    attr = await self.extract_attributes(text)
                    data = (
                        attr.model_dump() if hasattr(attr, "model_dump") else dict(attr)
                    )
                    f.write(json.dumps(data) + "\n")
                except Exception as e:
                    print(f"[Skipped] Item {i} due to error: {e}")
                    continue


if __name__ == "__main__":
    import asyncio

    asyncio.run(AtrributeExtractor().extract(csv_file="vapewholesalesusa_data.csv"))
