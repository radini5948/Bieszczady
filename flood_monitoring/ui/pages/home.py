import streamlit as st

st.title("System Monitorowania Zagrożeń Powodziowych")

st.markdown(
    """
### Witaj w systemie monitorowania zagrożeń powodziowych!

Ten system pozwala na:
- Przeglądanie stacji pomiarowych na mapie
- Monitorowanie poziomu wody i przepływu
- Analizę danych historycznych

Wybierz odpowiednią zakładkę z menu po lewej stronie, aby przejść do interesującej Cię sekcji.
"""
)

# Dodajemy informacje o autorach
with st.expander("O systemie"):
    st.markdown(
        """
    ### O systemie
    System został stworzony w ramach projektu na przedmiocie Programowanie Aplikacji Geoinformatycznych (Python).
    
    ### Technologie
    - Backend: FastAPI
    - Frontend: Streamlit
    - Dane: IMGW
    """
    )
