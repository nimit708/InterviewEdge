import deepl

auth_key = "498e4cbe-ed83-48d7-be50-40544b089627"  # Replace with your key
deepl_client = deepl.DeepLClient(auth_key)

result = deepl_client.translate_text("Hello, world!", target_lang="FR")
print(result.text)  # "Bonjour, le monde !"