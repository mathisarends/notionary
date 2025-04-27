from notionary.elements.block_element_registry_builder import BlockElementRegistryBuilder

if __name__ == "__main__":
    # Example usage of BlockElementRegistryBuilder to create a registry with all elements
    block_registry = (
        BlockElementRegistryBuilder()
        .start_standard()
        .build()
    )

    system_prompt = block_registry.generate_llm_prompt()
    print(system_prompt)