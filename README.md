<a href="https://www.linkedin.com/in/enistuna/"> 
  <img width="1280" height="180" alt="logo" src="project_documentation_files\graphics\v2.png" />
</a>

# <img width="42.58" height="14.75" alt="genuine icon" src="project_documentation_files/graphics/gen_icon.png" /> ***Genuine: Pragmatical Fintech Conversational AI***
**A Conversational AI that bridges the Pragmatic Gap by blending Pragmatical theories, Rule-Based systems and GenAI for Digital Banking Applications**

# **Contents**
*   **[Explanation of The Project](#explanation-of-the-project)**
    *   **[Theoretical Foundations](#theoretical-foundations)**
*   **[Details](#details)**
    *   **[Features](#1-features)**
    *   **[Tech Stack](#2-tech-stack)**
    *   **[Workflow](#3-workflow)**
    *   **[Dataflow](#4-dataflow)**
*   **[How to Use It?](#how-to-use-it)**
    *   **[Installation](#installation)**
*   **[Graphs and Visuals](#graphs-and-visuals)**
    *   **[Rasa Conversation Flow Diagram](#1-rasa-conversation-flow-diagram)**
    *   **[Pragmatic Network Graph](#2-pragmatic-network-graph)**
    *   **[Chatbot UI](#3-chatbot-ui)**
*   **[Explanation Video](#explanation-video)**
*   **[Notes & Acknowledgements](#notes--acknowledgements)**
*   **[References](#references)**

# **Explanation of The Project**

***Genuine*** is a specialized Turkish fintech conversational AI engineered to solve the problem of inability to grasp the contextual rules of human communication, for which I am calling the *Pragmatic Gap*. Operating as a hybrid engine, *Genuine* directly integrates Computational Pragmatics to decode non-literal intentions, ensuring strict transactional accuracy while significantly lowering the user's perceived risk barrier during face-threatening banking acts.

*   **Rule-Based**: Uses Rasa to deterministically track the dialogue state and maintain context without repetitive explicit confirmations.
*   **Generative**: Utilizes a RAG pipeline and Google Gemini AI to dynamically apply linguistic principles during conversational states.

    ## **Theoretical Foundations**

    This project is built upon three core pillars of Pragmatics:
    *   **Speech Act Theory:** Re-categorizing standard NLP intents (e.g., *Check Balance*) into classical Speech Acts (e.g., *Directives*) to inform the system's conversational tone.
    *   **The Gricean Maxims:** Utilizing a RAG pipeline to enforce the Cooperative Principle (Quantity, Quality, Relation, Manner), thereby constraining LLM verbosity and preventing cognitive overload.
    *   **Politeness Theory:** Algorithmically deploying *Negative Politeness* strategies to soften *Face-Threatening Acts (FTAs)* like loan rejections, which directly mitigates user trust issues and lowers the risk barrier.

# **Details**

## **1. Features**

*   **Pragmatic Competence**: Actively infers underlying user intentions rather than relying on rigid keyword mapping. It doesn't solely rely on rule-based algorithms.
*   **Gricean & Politeness Integration**: Algorithmically softens face-threatening acts to build user trust.
*   **Hybrid Architecture**: Seamlessly switches between strict banking operations (Rasa) and context-aware pragmatic reasoning (Gemini API + RAG).
*   **Linguistic Datasets**: Utilizes the **[GRICE](https://github.com/zilongzheng/grice-dataset)** dataset to build a semantic vector library for resolving implicatures, and the **[TrCOLA](https://github.com/turkish-nlp-suite/TrGLUE)** dataset for enforcing strict syntactic morphological guardrails via few-shot prompting.
*   **Implicit Confirmation**: Moves conversations forward efficiently without frustrating "Yes/No" verification loops.
*   **Modern UI**: Fully localized Turkish chat interface built with Chainlit.

## **2. Tech Stack**
Python - Rasa - Chainlit - LangChain - FastAPI - PyTorch - SQLite - SQLAlchemy - ChromaDB - Google Gemini API - Pydantic - Sentence-Transformers

## **3. Workflow**

1.  **User Input**: User sends a message.
2.  **Pragmatic Inference**: Rasa NLU analyzes the utterance to identify the true underlying intent.
3.  **State-Tracking & Routing**:
    *   **Direct Action**: Rasa Core triggers the Action Server for deterministic database queries via FastAPI.
    *   **Pragmatic Generation**: High-risk or complex inputs are routed to the RAG pipeline. The system retrieves pragmatic rules from ChromaDB and generates a contextually appropriate response via Google Gemini AI.
4.  **Response Delivery**: Pragmatically sound response is streamed to the user via the Chainlit frontend chat UI.

## **4. Dataflow**

*   **User** *>>* **Chainlit UI** *>>* **Rasa** 
    * *>>* **Action Server**
        *   *>>* **Backend Database**
        *   *>>* **RAG Pipeline** *>>* **LLM**

# **How to Use It?**

* If you want to test ***Genuine*** for yourself, you can access the chatbot in *Genuine's* **[Hugging Face Spaces](https://huggingface.co/spaces/enistuna/Genuine)** page. But if you want to try it locally, then proceed with the following steps:

    ## **Installation**

    ### **0. Prerequisites**
    *   **Python 3.10**
    *   **[Google Gemini API Key](https://aistudio.google.com/api-keys)**

    ### **1. Clone the Repository**
    ```bash
    git clone https://github.com/enistuna/Genuine.git
    cd Genuine/genuine_code
    ```

    ### **2. Install Dependencies**
    * Genuine uses two isolated virtual environments to prevent dependency conflicts between Rasa and Chainlit.

        #### **Environment A: Core (Backend & Rasa)**
        ```bash
        py -3.10 -m venv venv_core
        .\venv_core\Scripts\activate
        uv pip install -r requirements_core.txt
        ```

        #### **Environment B: UI (Frontend)**
        ```bash
        py -3.10 -m venv venv_ui
        .\venv_ui\Scripts\activate
        uv pip install -r requirements_ui.txt
        ```

    ### **3. Environment Setup**
    * First, get your **[Google Gemini API Key](https://aistudio.google.com/api-keys)** and then create a `.env` file in the `genuine_code` directory and add the following:
        ```ini
        GEMINI_API_KEY = API_KEY
        DATABASE_URL = sqlite:///./data/genuine.db
        ```

    ### **4. Running the Application**
    * You will need 4 separate terminals running simultaneously. Execute them in order. *Backend servers may take a while to boot up.*

        **Terminal 1 (Backend Database) - `venv_core`**
        ```bash
        .\venv_core\Scripts\activate
        python -m uvicorn src.backend.main:app --port 8001
        ```

        **Terminal 2 (Rasa Action Server) -  `venv_core`**
        ```bash
        .\venv_core\Scripts\activate
        python -m rasa run actions --actions src.rasa.actions --port 5055
        ```

        **Terminal 3 (Rasa Core Server) -  `venv_core`**
        ```bash
        .\venv_core\Scripts\activate
        python -m rasa run --enable-api --cors "*" --model src/rasa/models --endpoints src/rasa/endpoints.yml --credentials src/rasa/credentials.yml --port 5005
        ```

        **Terminal 4 (Frontend UI) -  `venv_ui`**
        ```bash
        .\venv_ui\Scripts\activate
        cd src/frontend
        python -m chainlit run app.py
        ```

# **Graphs and Visuals**

## **1. Rasa Conversation Flow Diagram**

The graph below illustrates the *Genuine*'s rule-based dialogue path a user can take without using GenAI features.

<img src="project_documentation_files\graphics\rasa_visualize_conversational_graph.png" alt="rasa visualize" />

## **2. Pragmatic Network Graph**

The graph below illustrates the neural architecture behind *Genuine*'s dialogue management. The system transfers the conversational data through an advanced pragmatic algorithm. [Gephi](https://gephi.org) is used to create this graph.

<img src="project_documentation_files\graphics\pragmatic_network_graph_white_background.png" height = 750 width = 750 alt="gephi pragmatic graph" />

## **3. Chatbot UI**

Chatbot UI is designed to look as sleek as possible.

[<img src="project_documentation_files\graphics\gen_interface_1.png" height = 436 width = 750 alt="chat UI 1" />](https://huggingface.co/spaces/enistuna/Genuine)

# **Explanation Video**
[<img src="project_documentation_files\graphics\thumbnail_v2.png" />](https://youtu.be/DZsXxEKgTe4?si=e9Xac_9LuukByNUU)

# **Notes & Acknowledgements**

* ***Genuine*** is the successor of **[Finchat](https://github.com/enistuna/Finchat)** project. 
* ***Genuine***'s development was supervised by Dr. Özgün Koşaner from Dokuz Eylül University's Department of Linguistics.
* I wrote my **[Bachelor's thesis paper](https://www.researchgate.net/publication/405988417_Introducing_Genuine_Pragmatical_Conversational_AI_for_Digital_Banking_and_Fintech_Applications)** on how improving a banking chatbot's pragmatic competancy will lead to better user experience through the lens of this graduation project.
* As of May 2026, ***[Genuine v1](https://github.com/enistuna/Genuine/releases/tag/v1.0)*** is finished being developed. This graduation project will likely get an update in the foreseeable future as it was granted **TÜBİTAK 2209-A program**'s support. Think of ***Genuine v1*** as the **first version** of the project as I iron out the wrinkles and make it more rigorous with the help of TÜBİTAK 2209-A program. I will be keeping everyone in the loop by adding more notes related to upcoming releases and versions.
* For any question, contribution or inquiry, **[send me an email](mailto:enissstuna@gmail.com)**.

# **References**

1.  Altinok, D. (2025). *Introducing TrGLUE and SentiTurca: A Comprehensive Benchmark for Turkish General Language Understanding and Sentiment Analysis*. arXiv preprint arXiv:2512.22100.

2. Attia, M., Muhamed, A., Alkhamissi, M., Solorio, T., & Diab, M. (2026, March). *Beyond Understanding: Evaluating the Pragmatic Gap in LLMs’ Cultural Processing of Figurative Language*. In Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers) (pp. 7238-7265).

3. Aydın, S., & Onaylı, E. (2020). *Bankacılıkta dijital dönüşümle değişen müşteri deneyimi: Müşteri sadakati, memnuniyeti ve tavsiye eğilimine yansımaları*. Yönetim ve Ekonomi Dergisi, 27(3), 645-663.

4. Balaji, K., Karim, S., & Rao, P. S. (2024, May). *Unleashing the power of smart chatbots: transforming banking with artificial intelligence*. In 2024 International Conference on Advances in Computing, Communication and Applied Informatics (ACCAI) (pp. 1-7). IEEE.

5. Bastian, M., Heymann, S., & Jacomy, M. (2009, March). *Gephi: an open source software for exploring and manipulating networks*. In Proceedings of the international AAAI conference on web and social media (Vol. 3, No. 1, pp. 361-362).

6. Bocklisch, T., Faulkner, J., Pawlowski, N., & Nichol, A. (2017). *Rasa: Open source language understanding and dialogue management*. arXiv preprint arXiv:1712.05181.

7. Bunt, H., & Black, W. (2000). *The ABC of Computational Pragmatics*.

8. Jurafsky, D. (2006). *Pragmatics and computational linguistics*. The handbook of pragmatics, 578-604.

9. Jwalapuram, P. (2017, September). *Evaluating dialogs based on Grice’s maxims*. In Proceedings of the Student Research Workshop associated with RANLP (pp. 17-24).

10. Kim, Y., Chin, B., Son, K., Kim, S., & Kim, J. (2025, April). *Applying the gricean maxims to a human-llm interaction cycle: Design insights from a participatory approach*. In Proceedings of the Extended Abstracts of the CHI Conference on Human Factors in Computing Systems (pp. 1-8).

11. Krause, L., & Vossen, P. T. (2024, September). *The Gricean maxims in NLP-a survey*. In Proceedings of the 17th international natural language generation conference (pp. 470-485).

12. Marak, Z. R., Pahari, S., Shekhar, R., & Tiwari, A. (2025). *Factors affecting chatbots in banking services: the UTAUT2 and innovation resistance theory perspective*. Journal of Innovation and Entrepreneurship, 14(1), 47.

13. Zheng, Z., Qiu, S., Fan, L., Zhu, Y., & Zhu, S. C. (2021, August). *Grice: A grammar-based dataset for recovering implicature and conversational reasoning*. In Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021 (pp. 2074-2085).
