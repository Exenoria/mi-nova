# mi-nova
esto es solo un llm que quiero presevar nada mas 

📦 Installation
1️⃣ Clone Repository
git clone https://github.com/Navjot-Singh7/Project-Nova.git
cd Project-Nova
2️⃣ Create Virtual Environment
py -3.11 -m venv my_env

my_env\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Install PyTorch (Required)
Example for NVIDIA GPU (CUDA 12.6):
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
5️⃣ Install Model directly from HuggingFace to your downloads folder (Recommended)
https://huggingface.co/Navpy/phi-3.5-AI-Vtuber-json/tree/main

6️⃣ Fix Modelfile for your system
Note - Copy the path where your model is downloaded and paste it in the Modelfile which is inside assistant_modelfile/ folder

# make sure it is inside quotes
FROM "<YOUR_MODEL_FILE_PATH>"
7️⃣ Create the Model - open your terminal in the Project-Nova folder and run this command
# Make sure you have ollama installed in your computer
ollama create nova -f assistant_modelfile/Modelfile
8️⃣ Check if the model is created or not
Note - You'll see your model name in the terminal

ollama list
9️⃣ Pull the Tool Calling Router Model
Nova uses qwen3.5:0.8b as a dedicated tool-calling router. Pull it via Ollama:

ollama pull qwen3.5:0.8b
🔟 Install Text Embedding model - this model is used for Retrieval Augmented Generation (RAG)
ollama pull nomic-embed-text
1️⃣1️⃣ Run the main Script normally
python main.py
By default, Project Nova runs in online mode to allow automatic downloading of required models (STT, TTS). Once all models are downloaded, you can run Nova fully offline by setting these environment variables at the top of your code in (main.py) and (web_ui.py) before importing anything.
import os
# Set offline mode BEFORE any other imports
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
