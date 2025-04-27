from notionary.elements.registry.block_element_registry_builder import (
    BlockElementRegistryBuilder,
)

if __name__ == "__main__":
    # Example usage of BlockElementRegistryBuilder to create a registry with all elements
    block_registry = BlockElementRegistryBuilder().create_full_registry()

    system_prompt = block_registry.generate_llm_prompt()
    print(system_prompt)
