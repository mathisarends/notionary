from notionary.core.converters.registry.block_element_registry import BlockElementRegistry

if __name__ == "__main__":
    prompt=BlockElementRegistry.generate_llm_prompt()
    print(prompt)