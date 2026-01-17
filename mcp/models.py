model_data = {
    'model_name': [
        'GPT-4', 
        'Claude 3.5 Sonnet', 
        'Llama 3 (70B)', 
        'Mistral 7B', 
        'Stable Diffusion XL', 
        'YOLOv8', 
        'Whisper V3', 
        'AlphaFold 2', 
        'BERT Large', 
        'Gemini 1.5 Pro'
    ],
    'task_type': [
        'NLP - Generative', 
        'NLP - Generative', 
        'NLP - Generative', 
        'NLP - Generative', 
        'Computer Vision - Generation', 
        'Computer Vision - Detection', 
        'Audio - Speech Recognition', 
        'Science - Protein Folding', 
        'NLP - Text Embedding', 
        'Multimodal - Generative'
    ],
    'framework': [
        'Cloud API', 
        'Cloud API', 
        'PyTorch/HuggingFace', 
        'PyTorch/GGUF', 
        'PyTorch/Diffusers', 
        'PyTorch/Ultralytics', 
        'PyTorch/OpenAI', 
        'JAX', 
        'PyTorch/HuggingFace', 
        'Cloud API'
    ],
    'deployment_environment': [
        'Cloud API', 
        'Cloud API', 
        'GPU Server', 
        'Edge/Laptop', 
        'GPU Server', 
        'Edge/Mobile', 
        'Server/Laptop', 
        'TPU/GPU Cluster', 
        'Server', 
        'Cloud API'
    ],
    'latency_score': [
        4.0,  # Slow due to large size
        6.0,  # Moderate/Fast token generation
        5.5,  # Requires heavy compute
        8.5,  # Fast on quantized hardware
        3.0,  # Slow generation time
        9.5,  # Real-time capable
        7.0,  # Moderate
        2.0,  # Very slow processing
        8.0,  # Fast inference
        5.0   # Moderate
    ],
    'accuracy_potential': [
        9.9,  # SOTA
        9.8,  # SOTA contender
        9.2,  # Excellent open source
        8.5,  # Good for size
        9.0,  # High quality images
        8.8,  # Good detection accuracy
        9.5,  # SOTA speech recognition
        9.9,  # Revolutionary accuracy
        8.0,  # Solid baseline
        9.7   # High multimodal accuracy
    ],
    'interpretability': [
        'Very Low', # Closed source
        'Very Low', # Closed source
        'Medium',   # Open weights, complex architecture
        'Medium',   # Open weights
        'Low',      # Diffusion process complex
        'Medium',   # Layer visualization possible
        'Low',      # Neural net black box
        'Low',      # Complex deep learning
        'Medium',   # Attention maps
        'Very Low'  # Closed source
    ]
}
