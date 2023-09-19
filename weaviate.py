import weaviate

# Instantiate the client with the auth config
client = weaviate.Client(
    url="https://travel-pb-cluster-mfso2mhk.weaviate.network",  # Replace w/ your endpoint
    auth_client_secret=weaviate.AuthApiKey(api_key="jVRRFvwW7iwiHhhOSbpUOnM2tPYYpaGHOy11"),  # Replace w/ your Weaviate instance API key
)