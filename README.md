# Summarize your favorite Maths article !

This project aims to help researchers in Mathematics in getting a concise but technically precise summarization of the articles on arXiv. Since reading articles is one of the main activities of a Mathematician, having a tool that gives a brief but mathematically precise summary helps in taking the decision to dive fully in the article or not. It requires the arXiv reference of the article (the 9 numbers as in arXiv:1234.56789) as well as the name of the article. 

This tool makes use of the latest OpenAI GPT model, namely 'gpt-4-turbo' ; and so it requires that you enter your own OpenAI api key. Symply replace the sequence between the quotations marks in 'utils.py':

    openai_api_key = "Replace with your api key"
   
   Having ensured that all the required packages are installed (see the requirements.txt file), run in a terminal:

    streamlit run path_to_files/main.py


where 'path_to_files' is the path to the downloaded code files. This will open a window in your browser, then simply fill the reference and the name of the article to get your summary ! 

# Warning

Running the app will download the source files from the arXiv website, but will not keep them in memory. At the moment, the code handles .gz or .tar.gz files downloaded from the TeX source. 
