import streamlit as st
from utils import answer_with_rag


def main():
    st.set_page_config(page_title='Summarize your favorite Maths paper !')
    st.title('Summarize your favorite Maths paper !')
    reference = st.text_input('Enter the arXiv reference')
    article_name = st.text_input('Enter the name of the article')
    if st.button("Generate"):
        if reference and article_name:
            result = answer_with_rag(reference, article_name)
            st.write(result)
        else:
            st.write("Please fill in both fields.")


if __name__ == '__main__':
    main()
